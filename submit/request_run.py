#!/usr/bin/env python3
"""Create 2024 NanoTuples JDLs from samples/<datasetname>/<prepid>/dataset."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

PACKAGE = Path(__file__).resolve().parents[1]
SUBMIT = Path(__file__).resolve().parent
SAMPLES = PACKAGE / "samples"
X509UP = SUBMIT / "x509up"
OUTPUT_ROOT = "root://cceos.ihep.ac.cn:1094//store/user/zkou"
SAFE_FIELD = re.compile(r"^[A-Za-z0-9_./:+-]+$")


def safe_field(value: str) -> str:
    if not SAFE_FIELD.fullmatch(value):
        raise ValueError(f"Unsupported character in Condor queue value: {value!r}")
    return value


def input_uri(name: str) -> str:
    if name.startswith("file:"):
        name = name[5:]
    if name.startswith("/store/"):
        name = "root://cms-xrd-global.cern.ch/" + name
    if not name.startswith("root://"):
        raise ValueError(f"Expected an LFN or root:// file path: {name}")
    return safe_field(name)


def generate_x509up() -> Path:
    valid = subprocess.run(
        ["voms-proxy-info", "-file", str(X509UP), "-exists"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    if not valid and subprocess.run([str(SUBMIT / "x509up-gen")]).returncode:
        raise RuntimeError("error generating x509 user proxy")
    return X509UP


def scan_dataset(dataset: str, proxy: Path) -> list[dict]:
    if dataset.startswith("file:"):
        dataset = dataset[5:]
    records = []
    if dataset.startswith("root://"):
        url = urlsplit(dataset)
        server = f"root://{url.netloc}"
        result = subprocess.run(
            ["xrdfs", server, "ls", url.path], check=True, text=True, capture_output=True,
            env={**os.environ, "X509_USER_PROXY": str(proxy)},
        )
        for line in result.stdout.splitlines():
            path = line.strip()
            if path.endswith(".root"):
                name = path if path.startswith("root://") else server + "//" + path.lstrip("/")
                records.append({"file": [{"name": name}]})
    else:
        if not dataset.startswith("/"):
            raise ValueError(f"Expected a DAS dataset or root:// directory: {dataset}")
        query = f"file dataset={dataset} instance=prod/global | grep file.name,file.nevents"
        result = subprocess.run(
            ["dasgoclient", "-query", query, "-limit=0"],
            text=True, capture_output=True,
            env={**os.environ, "X509_USER_PROXY": str(proxy)},
        )
        if result.returncode or not result.stdout.strip():
            result = subprocess.run(
                ["dasgoclient", "-query", f"file dataset={dataset} instance=prod/global | grep file.name", "-limit=0"],
                check=True, text=True, capture_output=True,
                env={**os.environ, "X509_USER_PROXY": str(proxy)},
            )
        for line in result.stdout.splitlines():
            fields = line.split()
            if not fields or not fields[0].startswith("/store/"):
                raise ValueError(f"Unexpected DAS file row: {line!r}")
            file = {"name": fields[0]}
            if len(fields) > 1:
                try:
                    file["nevents"] = int(fields[1])
                except ValueError:
                    pass
            records.append({"file": [file]})
    if not records:
        raise RuntimeError(f"No ROOT files found for {dataset}")
    return records


def sample_files(directory: Path, proxy: Path, force: bool = False) -> list[dict]:
    path = directory / "filelist"
    if path.is_file() and not force:
        return json.loads(path.read_text())
    dataset_file = directory / "dataset"
    datasets = [line.strip() for line in dataset_file.read_text().splitlines() if line.strip()]
    if not datasets:
        raise ValueError(f"Empty dataset file: {dataset_file}")
    records = []
    for dataset in datasets:
        print(f"Scanning {dataset}")
        records.extend(scan_dataset(dataset, proxy))
    temporary = directory / "filelist.tmp"
    temporary.write_text(json.dumps(records, separators=(",", ":")) + "\n")
    temporary.replace(path)
    return records


def count_events(name: str) -> int:
    import uproot

    with uproot.open(input_uri(name), timeout=30) as root_file:
        return int(root_file["Events"].num_entries)


def fill_nevents(directory: Path, records: list[dict], proxy: Path) -> None:
    missing = [item["file"][0] for item in records if item["file"][0].get("nevents", -1) < 0]
    if not missing:
        return

    previous_proxy = os.environ.get("X509_USER_PROXY")
    os.environ["X509_USER_PROXY"] = str(proxy)
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
            for start in range(0, len(missing), 200):
                batch = missing[start:start + 200]
                futures = {pool.submit(count_events, record["name"]): record for record in batch}
                errors = []
                for future in concurrent.futures.as_completed(futures):
                    record = futures[future]
                    try:
                        record["nevents"] = future.result()
                        print(f"{record['name']}: {record['nevents']} Events", flush=True)
                    except Exception as error:
                        print(f"Failed to count Events: {record['name']}: {error}", flush=True)
                        errors.append(f"{record['name']}: {error}")
                path = directory / "filelist"
                temporary = directory / "filelist.tmp"
                temporary.write_text(json.dumps(records, separators=(",", ":")) + "\n")
                temporary.replace(path)
                if errors:
                    raise RuntimeError("Could not read Events in " + "; ".join(errors[:3]))
    finally:
        if previous_proxy is None:
            os.environ.pop("X509_USER_PROXY", None)
        else:
            os.environ["X509_USER_PROXY"] = previous_proxy


def make_parser(default_output_kind: str = "full") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("datasetname", help="directory name under samples/")
    parser.add_argument("prepid", help="directory name under samples/<datasetname>/")
    parser.add_argument("--output-kind", choices=("full", "slim"), default=default_output_kind)
    parser.add_argument("--events", type=int, help="maximum events per file")
    parser.add_argument("--max-files", type=int)
    parser.add_argument("--nolog", action="store_true", help="use Run 2 overwritten log names")
    return parser


def main(default_output_kind: str = "full") -> None:
    args = make_parser(default_output_kind).parse_args()
    if any(value in {"", ".", ".."} or "/" in value for value in (args.datasetname, args.prepid)):
        raise ValueError("datasetname and prepid must be sample directory names")
    if args.events is not None and args.events < 1:
        raise ValueError("--events must be positive")
    if args.max_files is not None and args.max_files < 1:
        raise ValueError("--max-files must be positive")

    safe_field(args.datasetname)
    safe_field(args.prepid)
    directory = SAMPLES / args.datasetname / args.prepid
    dataset_file = directory / "dataset"
    if not dataset_file.is_file():
        raise FileNotFoundError(dataset_file)
    datasets = [line.strip() for line in dataset_file.read_text().splitlines() if line.strip()]
    if not datasets:
        raise ValueError(f"Empty dataset file: {dataset_file}")
    isdata = all(dataset.rstrip("/").endswith("/MINIAOD") for dataset in datasets)
    mode = "data" if isdata else "mc"
    prog = SUBMIT / f"run-{mode}-2024{'-slim' if args.output_kind == 'slim' else ''}.sh"
    proxy = generate_x509up()
    all_records = sample_files(directory, proxy)
    if not all_records:
        raise RuntimeError(f"Empty filelist: {directory / 'filelist'}")
    fill_nevents(directory, all_records, proxy)
    records = all_records[:args.max_files]

    product = "CustomizedNanoAOD-slim" if args.output_kind == "slim" else "CustomizedNanoAOD"
    output_dir = "/".join((OUTPUT_ROOT, product, "V0", "2024", "Data" if isdata else "MC", args.datasetname, args.prepid))
    logdir = SUBMIT / "log" / args.datasetname / args.prepid
    logdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in records:
        file = item["file"][0]
        name = input_uri(file["name"])
        basename = Path(urlsplit(name).path).name
        nevents = int(file["nevents"])
        if args.events is not None:
            nevents = min(args.events, nevents) if nevents > 0 else args.events
        output = safe_field(output_dir + "/" + basename.replace("MiniAODv6", "CustomizedNanoAODv15"))
        logprefix = logdir / ("overwritten" if args.nolog else Path(basename).stem)
        rows.append(f"{nevents}, {name}, {output}, {logprefix}")

    jdl_dir = SUBMIT / "jdl"
    jdl_dir.mkdir(exist_ok=True)
    suffix = "_slim" if args.output_kind == "slim" else ""
    jdl = jdl_dir / f"{args.datasetname}_{args.prepid}{suffix}.jdl"
    lines = [
        "Universe = vanilla",
        f"Executable = {prog}",
        "",
        '+ProjectName="cms.org.cern"',
        "",
        f"X509UP = {proxy}",
        "NTHREAD = 8",
        "Arguments = $(NEVENT) $(NTHREAD) $(FILEIN) $(FILEOUT)",
        "",
        "request_cpus = 8",
        "request_memory = 4096",
        "use_x509userproxy = True",
        "x509userproxy = $(X509UP)",
        "",
        "on_exit_remove        = (ExitBySignal == False) && (ExitCode == 0)",
        "on_exit_hold          = (ExitBySignal == True) || (ExitCode != 0)",
        'on_exit_hold_reason   = strcat("Job held by ON_EXIT_HOLD due to ", ifThenElse((ExitBySignal == True), strcat("exit signal ", ExitSignal), strcat("exit code ", ExitCode)), ".")',
        "periodic_release      = (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 60*60)",
        "",
        "+MaxRuntime = 4*60*60",
        "",
        "Log    = $(LOGPREFIX).log",
        "Output = $(LOGPREFIX)_1.log",
        "Error  = $(LOGPREFIX)_2.log",
        "",
        "should_transfer_files = YES",
        f"transfer_input_files = {SUBMIT / 'run_nano.sh'}",
        'transfer_output_files = ""',
        "Queue NEVENT, FILEIN, FILEOUT, LOGPREFIX from (",
        *rows,
        ")",
        "",
    ]
    jdl.write_text("\n".join(lines))
    print(f"Prepared {len(rows)} {mode} {args.output_kind} job(s): {jdl}")
    print(f"Submit with: condor_submit {jdl.relative_to(SUBMIT)}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, RuntimeError, subprocess.CalledProcessError, KeyError) as error:
        raise SystemExit(f"error: {error}") from None
