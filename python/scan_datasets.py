#!/usr/bin/env python3
"""Scan the 2024 MC manifests under samples/<datasetname>/<prepid>."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import subprocess
from pathlib import Path

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def scan(directory: Path, force: bool) -> tuple[str, str, str]:
    dataset = (directory / "dataset").read_text().strip()
    instance = (directory / "dbs_instance").read_text().strip()
    expected = json.loads((directory / "expected_summary.json").read_text())
    label = f"{directory.parent.name}/{directory.name}"
    output = directory / "filelist"
    result_path = directory / "scan.json"
    error_path = directory / "scan_error.json"
    if output.is_file() and result_path.is_file() and not force:
        result = json.loads(result_path.read_text())
        return label, "skipped", f"{result['nfiles']} files"

    command = [
        "dasgoclient",
        "-query", f"file dataset={dataset} instance={instance} | grep file.name,file.nevents",
        "-limit=0",
    ]
    temp = directory / "filelist.tmp"
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=True, timeout=900)
        names: set[str] = set()
        records: list[tuple[str, int]] = []
        for line in completed.stdout.splitlines():
            fields = line.split()
            if len(fields) != 2 or not fields[0].startswith("/store/"):
                raise ValueError(f"Unexpected DAS file row: {line!r}")
            name, nevents = fields[0], int(fields[1])
            if name in names:
                raise ValueError(f"Duplicate DAS file: {name}")
            names.add(name)
            records.append((name, nevents))
        if not records:
            raise ValueError("DAS returned no files")

        with temp.open("w", encoding="utf-8") as stream:
            json.dump([{"file": [{"name": name, "nevents": nevents}]} for name, nevents in records], stream, separators=(",", ":"))
            stream.write("\n")
        temp.replace(output)
        nfiles = len(records)
        nevents = sum(value for _, value in records)
        matches = nfiles == expected["nfiles"] and nevents == expected["nevents"]
        result = {
            "dataset": dataset,
            "dbs_instance": instance,
            "scanned_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "nfiles": nfiles,
            "nevents": nevents,
            "expected_nfiles": expected["nfiles"],
            "expected_nevents": expected["nevents"],
            "matches_expected": matches,
        }
        result_path.write_text(json.dumps(result, indent=2) + "\n")
        error_path.unlink(missing_ok=True)
        return label, "ok" if matches else "mismatch", f"{nfiles} files, {nevents} events"
    except Exception as error:
        temp.unlink(missing_ok=True)
        error_path.write_text(json.dumps({"dataset": dataset, "dbs_instance": instance, "error": str(error)}, indent=2) + "\n")
        return label, "error", str(error)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--only", help="scan one datasetname or prep ID")
    parser.add_argument("--force", action="store_true", help="replace previous scan results")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    directories = sorted(path.parent for path in SAMPLES.glob("*/*/dataset"))
    if args.only:
        directories = [d for d in directories if args.only in (d.parent.name, d.name)]
    if not directories:
        parser.error("No matching sample directories")

    counts = {"ok": 0, "mismatch": 0, "error": 0, "skipped": 0}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(scan, directory, args.force) for directory in directories]
        for future in concurrent.futures.as_completed(futures):
            label, status, detail = future.result()
            counts[status] += 1
            print(f"{status}: {label}: {detail}", flush=True)
    print(f"Scanned {len(directories)} sample directories: {counts}", flush=True)
    if counts["error"] or counts["mismatch"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
