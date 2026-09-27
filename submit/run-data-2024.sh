#!/usr/bin/env bash
set -euo pipefail
export NANO_MODE=data
export NANO_OUTPUT_KIND=full
export NANO_ERA=Run3_2024
export NANO_CONDITIONS=150X_dataRun3_v2
export NANO_CONTENT=NANOAOD
export NANO_CUSTOMISE=PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData
exec "$(dirname "$0")/run_nano.sh" "$@"
