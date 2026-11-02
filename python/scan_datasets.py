#!/usr/bin/env python3
"""Populate filelist for sample directories that have a dataset file."""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE / "submit"))
from request_run import fill_nevents, generate_x509up, sample_files


def scan(directory: Path, proxy: Path, force: bool) -> tuple[str, str, str]:
    label = f"{directory.parent.name}/{directory.name}"
    cached = (directory / "filelist").is_file()
    try:
        records = sample_files(directory, proxy, force=force)
        fill_nevents(directory, records, proxy)
        status = "cached" if cached and not force else "scanned"
        return label, status, f"{len(records)} files"
    except Exception as error:
        return label, "error", str(error)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--only", help="scan one datasetname or prep id")
    parser.add_argument("--force", action="store_true", help="refresh an existing filelist")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    directories = sorted(path.parent for path in (PACKAGE / "samples").glob("*/*/dataset"))
    if args.only:
        directories = [d for d in directories if args.only in (d.parent.name, d.name)]
    if not directories:
        parser.error("No matching sample directories")

    proxy = generate_x509up()
    counts = {"cached": 0, "scanned": 0, "error": 0}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(scan, directory, proxy, args.force) for directory in directories]
        for future in concurrent.futures.as_completed(futures):
            label, status, detail = future.result()
            counts[status] += 1
            print(f"{status}: {label}: {detail}", flush=True)
    print(f"Checked {len(directories)} samples: {counts}", flush=True)
    if counts["error"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
