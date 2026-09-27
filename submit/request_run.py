#!/usr/bin/env python3
"""Prepare file-based CMSSW 15 NanoTuples HTCondor jobs."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import tarfile
from pathlib import Path
from urllib.parse import urlsplit

PACKAGE = Path(__file__).resolve().parents[1]
SUBMIT = Path(__file__).resolve().parent
SAFE_FIELD = re.compile(r"^[A-Za-z0-9_./:+-]+$")
MODEL_ASSETS = (
    "data/InclParticleTransformer-MD/ak15/V02_xggg_finetune/preprocess_corr.json",
    "data/InclParticleTransformer-MD/ak15/V02_xggg_finetune/model.onnx",
    "data/InclParticleTransformer-MD/ak8/V03FullScore/model_full_score.onnx",
)


def slug(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    if not result:
        raise ValueError("An empty job or sample name is not allowed")
    return result[:100]


def safe_field(value: str) -> str:
    if not SAFE_FIELD.fullmatch(value):
        raise ValueError(f"Unsupported character in Condor queue value: {value!r}")
    return value


def input_uri(value: str) -> str:
    if value.startswith("root://"):
        return safe_field(value)
    if value.startswith("/store/"):
        return safe_field("root://cms-xrd-global.cern.ch/" + value)
    if value.startswith("file:"):
        value = value[5:]
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(f"Input must be an absolute path, LFN, or root URL: {value}")
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    if str(resolved).startswith("/eos/"):
        return safe_field("root://eosuser.cern.ch/" + str(resolved))
    raise ValueError(f"Local input must resolve under /eos for batch workers: {resolved}")


def output_uri(value: str) -> str:
    if value.startswith("root://"):
        return safe_field(value.rstrip("/"))
    path = Path(value)
    if not path.is_absolute():
        raise ValueError("Output directory must be an EOS absolute path or root URL")
    resolved = path.resolve()
    if not str(resolved).startswith("/eos/"):
        raise ValueError("Local output directory must resolve under /eos")
    return safe_field("root://eosuser.cern.ch/" + str(resolved).rstrip("/"))


def dataset_inputs(dataset: str, mode: str, limit: int | None, proxy: Path, instance: str) -> list[tuple[str, str]]:
    fields = dataset.strip("/").split("/")
    tier = "MINIAOD" if mode == "data" else "MINIAODSIM"
    if len(fields) != 3 or fields[2] != tier or "2024" not in dataset:
        raise ValueError(f"Expected a 2024 /primary/campaign/{tier} dataset")
    command = [
        "dasgoclient",
        "-query", f"file dataset={dataset} instance={instance} | grep file.name",
        f"-limit={limit or 0}",
    ]
    try:
        result = subprocess.run(
            command, check=True, text=True, capture_output=True,
            env={**os.environ, "X509_USER_PROXY": str(proxy)},
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"DAS query failed: {error.stderr.strip()}") from error
    lfns = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lfns:
        raise RuntimeError(f"DAS returned no files for {dataset}")
    return [(fields[0], input_uri(lfn)) for lfn in lfns]


def list_inputs(path: Path, label: str) -> list[tuple[str, str]]:
    values = [
        line.split("#", 1)[0].strip()
        for line in path.read_text().splitlines()
    ]
    return [(label, input_uri(value)) for value in values if value]


def missing_assets() -> list[str]:
    return [name for name in MODEL_ASSETS if not (PACKAGE / name).is_file()]


def check_proxy(path: Path) -> None:
    try:
        result = subprocess.run(
            ["voms-proxy-info", "--file", str(path), "-timeleft"],
            check=True, text=True, capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise RuntimeError(f"No valid grid proxy at {path}; run voms-proxy-init --voms cms") from error
    if int(result.stdout.strip()) < 3600:
        raise RuntimeError(f"Grid proxy expires in under an hour: {path}")


def snapshot(path: Path) -> None:
    with tarfile.open(path, "w:gz", dereference=True) as archive:
        for item in sorted(PACKAGE.rglob("*")):
            if not item.is_file():
                continue
            rel = item.relative_to(PACKAGE)
            parts = rel.parts
            if (
                ".git" in parts or "__pycache__" in parts
                or parts[0] == "samples"
                or (parts[0] == "submit" and rel.as_posix() not in (
                    "submit/slim_nano.py", "submit/keep_and_drop_2024.txt"
                ))
                or "log" in parts
                or item.suffix in (".pyc", ".root", ".jdl")
                or item.name.startswith("x509up")
            ):
                continue
            archive.add(item, arcname="NanoTuples/" + rel.as_posix(), recursive=False)


def make_parser(default_output_kind: str = "full") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("data", "mc"), required=True)
    parser.add_argument("--year", choices=("2024",), default="2024")
    parser.add_argument("--dbs-instance", choices=("prod/global", "prod/phys03"), default="prod/global",
                        help="DBS instance for --dataset; DY samples may need prod/phys03")
    parser.add_argument("--output-kind", choices=("full", "slim"), default=default_output_kind,
                        help="full customized NanoAOD or old-style 0L/1L/2L slimmed NanoAOD")
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--dataset", help="2024 DAS MiniAOD dataset")
    sources.add_argument("--input-list", type=Path, help="one LFN, root URL, or EOS file path per line")
    sources.add_argument("--input-file", action="append", help="repeat for explicit LFN, root URL, or EOS files")
    parser.add_argument("--name", help="job name and output group")
    parser.add_argument("--output-dir", required=True, help="EOS directory or root URL")
    parser.add_argument("--job-dir", type=Path, help="where to write JDL, snapshot, and logs")
    parser.add_argument("--events", type=int, default=-1, help="maximum events per file; -1 runs the whole file")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--memory-mb", type=int, default=8000)
    parser.add_argument("--max-runtime", type=int, default=8 * 3600, help="seconds")
    parser.add_argument("--max-files", type=int, help="limit the number of input files")
    parser.add_argument("--scram-arch", default=os.environ.get("SCRAM_ARCH", "el9_amd64_gcc12"))
    parser.add_argument("--proxy", type=Path, default=Path(
        os.environ.get("X509_USER_PROXY", f"/tmp/x509up_u{os.getuid()}")
    ))
    parser.add_argument("--requirements", help="optional HTCondor requirements expression")
    parser.add_argument("--submit", action="store_true", help="submit the prepared JDL to HTCondor")
    return parser


def main(default_output_kind: str = "full") -> None:
    args = make_parser(default_output_kind).parse_args()
    if args.events == 0 or args.events < -1:
        raise ValueError("--events must be -1 or positive")
    if args.threads < 1 or args.memory_mb < 1 or args.max_runtime < 1:
        raise ValueError("Threads, memory, and runtime must be positive")
    if args.max_files is not None and args.max_files < 1:
        raise ValueError("--max-files must be positive")
    safe_field(args.scram_arch)
    if args.requirements and ("\n" in args.requirements or "\r" in args.requirements):
        raise ValueError("--requirements must be a single line")
    if args.dataset:
        check_proxy(args.proxy)
        inputs = dataset_inputs(args.dataset, args.mode, args.max_files, args.proxy, args.dbs_instance)
        name = args.name or args.dataset.strip("/").split("/")[0]
    elif args.input_list:
        name = args.name or args.input_list.stem
        inputs = list_inputs(args.input_list.resolve(), name)
    else:
        name = args.name or "files"
        inputs = [(name, input_uri(value)) for value in args.input_file]
    inputs = inputs[:args.max_files]
    if not inputs:
        raise ValueError("No input files selected")

    missing = missing_assets()
    if args.submit:
        if missing:
            raise RuntimeError("Configured models/preprocessing are missing: " + ", ".join(missing))
        check_proxy(args.proxy)

    output_base = output_uri(args.output_dir)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_name = slug(name + ("_slim" if args.output_kind == "slim" else "")) + "_" + timestamp
    job_dir = (args.job_dir or SUBMIT / "jobs" / run_name).resolve()
    job_dir.mkdir(parents=True, exist_ok=False)
    (job_dir / "logs").mkdir()

    tarball = job_dir / "nanotuples_snapshot.tar.gz"
    snapshot(tarball)
    rows = []
    for index, (label, source) in enumerate(inputs, start=1):
        stem = slug(Path(urlsplit(source).path).stem)
        suffix = "_nano_slim.root" if args.output_kind == "slim" else "_nano.root"
        dest = f"{output_base}/{run_name}/{slug(label)}/{index:05d}_{stem}{suffix}"
        rows.append(f"{args.events}, {safe_field(source)}, {safe_field(dest)}")

    version = PACKAGE.parents[2].name
    if not re.fullmatch(r"CMSSW_[0-9_]+", version):
        raise RuntimeError(f"Could not derive CMSSW version from {PACKAGE}")
    executable = SUBMIT / f"run-{args.mode}-{args.year}{'-slim' if args.output_kind == 'slim' else ''}.sh"
    if not executable.is_file():
        raise FileNotFoundError(executable)
    jdl = job_dir / "nano.jdl"
    lines = [
        "universe = vanilla",
        f"executable = {executable}",
        "transfer_executable = True",
        "arguments = $(NEVENT) $(THREADS) $(FILEIN) $(FILEOUT)",
        f"THREADS = {args.threads}",
        f'environment = "CMSSW_VERSION={version} SCRAM_ARCH={args.scram_arch}"',
        f"request_cpus = {args.threads}",
        f"request_memory = {args.memory_mb}",
        f"request_disk = 12000",
        f"+MaxRuntime = {args.max_runtime}",
        "use_x509userproxy = True",
        f"x509userproxy = {args.proxy.resolve()}",
        "should_transfer_files = YES",
        "when_to_transfer_output = ON_EXIT",
        f"transfer_input_files = {tarball}, {SUBMIT / 'run_nano.sh'}",
        'transfer_output_files = ""',
        "on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)",
        f"Log = {job_dir / 'logs' / '$(ClusterId).$(ProcId).log'}",
        f"Output = {job_dir / 'logs' / '$(ClusterId).$(ProcId).out'}",
        f"Error = {job_dir / 'logs' / '$(ClusterId).$(ProcId).err'}",
    ]
    if args.requirements:
        lines.append(f"requirements = {args.requirements}")
    lines.extend(["", "queue NEVENT, FILEIN, FILEOUT from (", *rows, ")", ""])
    jdl.write_text("\n".join(lines))

    print(f"Prepared {len(inputs)} {args.mode} {args.output_kind} job(s): {jdl}")
    print(f"Code snapshot: {tarball}")
    if missing:
        print("Configured assets still missing: " + ", ".join(missing))
    if args.submit:
        subprocess.run(["condor_submit", str(jdl)], check=True)
    elif missing:
        print("Install the configured assets and renew the grid proxy before submitting this JDL.")
    else:
        print(f"Review then submit with: condor_submit {jdl}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, RuntimeError) as error:
        raise SystemExit(f"error: {error}") from None
