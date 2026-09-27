#!/usr/bin/env bash
set -euo pipefail
export NANO_MODE=mc
export NANO_OUTPUT_KIND=slim
export NANO_ERA=Run3_2024
export NANO_CONDITIONS=150X_mcRun3_2024_realistic_v2
export NANO_CONTENT=NANOAODSIM
export NANO_CUSTOMISE=PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC
exec "$(dirname "$0")/run_nano.sh" "$@"
