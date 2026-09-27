#!/usr/bin/env python3
"""Prepare slimmed NanoTuples jobs; accepts request_run.py options except --output-kind."""

import sys

from request_run import main


if __name__ == "__main__":
    if any(arg == "--output-kind" or arg.startswith("--output-kind=") for arg in sys.argv[1:]):
        raise SystemExit("request_run_slim.py always selects slim; use request_run.py to choose --output-kind")
    main(default_output_kind="slim")
