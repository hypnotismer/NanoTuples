#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
    echo "Usage: $0 <events> <threads> <input> <output-root-url>" >&2
    exit 2
fi

: "${NANO_MODE:?Use one of the year/mode-specific run-*-2024*.sh scripts}"
: "${NANO_OUTPUT_KIND:?Output kind is not set}"
: "${NANO_ERA:?Era is not set}"
: "${NANO_CONDITIONS:?Conditions are not set}"
: "${NANO_CONTENT:?Event content is not set}"
: "${NANO_CUSTOMISE:?Customise function is not set}"
if [[ "$NANO_MODE" != mc && "$NANO_MODE" != data ]]; then
    echo "NANO_MODE must be mc or data" >&2
    exit 2
fi
if [[ "$NANO_OUTPUT_KIND" != full && "$NANO_OUTPUT_KIND" != slim ]]; then
    echo "NANO_OUTPUT_KIND must be full or slim" >&2
    exit 2
fi
events=$1
threads=$2
filein=$3
fileout=$4

if [[ "$fileout" != root://* ]]; then
    echo "Output must be a root:// URL" >&2
    exit 2
fi

workdir=${_CONDOR_SCRATCH_DIR:-$PWD}
cd "$workdir"
if [[ ! -s nanotuples_snapshot.tar.gz ]]; then
    echo "NanoTuples snapshot was not transferred" >&2
    exit 1
fi
if [[ -n "${X509_USER_PROXY:-}" ]]; then
    voms-proxy-info -timeleft
fi

source /cvmfs/cms.cern.ch/cmsset_default.sh
cmssw_version=${CMSSW_VERSION:-CMSSW_15_0_10}
export SCRAM_ARCH=${SCRAM_ARCH:-el9_amd64_gcc12}
cmsrel "$cmssw_version"
mkdir -p "$cmssw_version/src/PhysicsTools"
tar -xzf nanotuples_snapshot.tar.gz -C "$cmssw_version/src/PhysicsTools"
cd "$cmssw_version/src"
eval "$(scram runtime -sh)"

model_dir=PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak15/V02_xggg_finetune
for asset in "$model_dir/preprocess_corr.json" "$model_dir/model.onnx" \
    PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak8/V03FullScore/model_full_score.onnx; do
    if [[ ! -s "$asset" ]]; then
        echo "Configured model asset missing: $asset" >&2
        exit 1
    fi
done

scram b -j "$threads"

if [[ "$NANO_MODE" == mc ]]; then
    mode_flag=--mc
else
    mode_flag=--data
fi

cmsDriver.py \
    "$mode_flag" \
    -n "$events" \
    --nThreads "$threads" \
    --python_filename "$workdir/nano_cfg.py" \
    --eventcontent "$NANO_CONTENT" \
    --datatier "$NANO_CONTENT" \
    --conditions "$NANO_CONDITIONS" \
    --step NANO \
    --scenario pp \
    --era "$NANO_ERA" \
    --customise "$NANO_CUSTOMISE" \
    --filein "$filein" \
    --fileout "file:$workdir/nano.root" \
    --no_exec

cmsRun "$workdir/nano_cfg.py"
test -s "$workdir/nano.root"
output_file="$workdir/nano.root"
if [[ "$NANO_OUTPUT_KIND" == slim ]]; then
    python3 PhysicsTools/NanoTuples/submit/slim_nano.py "$output_file" "$workdir/nano_slim.root"
    test -s "$workdir/nano_slim.root"
    output_file="$workdir/nano_slim.root"
    rm "$workdir/nano.root"
fi

remote=${fileout#root://}
server=${remote%%/*}
remote_path=${remote#*/}
if [[ "$remote_path" != /* ]]; then
    remote_path="/$remote_path"
fi
xrdfs "root://$server" mkdir -p "${remote_path%/*}"
xrdcp --nopbar -f "$output_file" "$fileout"
