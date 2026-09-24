#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 5 ]]; then
    echo "Usage: $0 <data|mc> <events> <threads> <input> <output-root-url>" >&2
    exit 2
fi

mode=$1
events=$2
threads=$3
filein=$4
fileout=$5
if [[ "$mode" != data && "$mode" != mc ]]; then
    echo "Mode must be data or mc" >&2
    exit 2
fi
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

if [[ "$mode" == mc ]]; then
    mode_flag=--mc
    content=NANOAODSIM
    conditions=150X_mcRun3_2024_realistic_v2
    customise=PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC
else
    mode_flag=--data
    content=NANOAOD
    conditions=150X_dataRun3_v2
    customise=PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData
fi

cmsDriver.py \
    "$mode_flag" \
    -n "$events" \
    --nThreads "$threads" \
    --python_filename "$workdir/nano_cfg.py" \
    --eventcontent "$content" \
    --datatier "$content" \
    --conditions "$conditions" \
    --step NANO \
    --scenario pp \
    --era Run3_2024 \
    --customise "$customise" \
    --filein "$filein" \
    --fileout "file:$workdir/nano.root" \
    --no_exec

cmsRun "$workdir/nano_cfg.py"
test -s "$workdir/nano.root"

remote=${fileout#root://}
server=${remote%%/*}
remote_path=${remote#*/}
if [[ "$remote_path" != /* ]]; then
    remote_path="/$remote_path"
fi
xrdfs "root://$server" mkdir -p "${remote_path%/*}"
xrdcp --nopbar -f "$workdir/nano.root" "$fileout"
