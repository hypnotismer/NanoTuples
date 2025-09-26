#!/bin/bash

# Avoid "input: $HOME/.root.mimes, output: $HOME/.root.mimes" error.
# REF: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCrabFaq
if [ -z "${HOME}" ]; then
    export HOME="$(pwd)"
fi

if [ $# -lt 3 ]; then
    >&2 echo "usage: $(basename "$0") <nevent> <nthread> <file-in> <file-out>"
    exit 1
fi
NEVENT="$1"
NTHREAD="$2"
FILEIN="$3"
FILEOUT="$4"
filename=$(basename "$FILEOUT")
mkdir -p tmp

if [ -z "${FILEOUT}" ]; then
    FILEOUT="${FILEIN/MiniAODv2/CustomizedNanoAODv15}"
fi
if [ "${FILEIN:0:7}" != "root://" ]; then FILEIN="file:${FILEIN}"; fi
if [ "${FILEOUT:0:7}" != "root://" ]; then FILEOUT="file:${FILEOUT}"; fi

set -ev
voms-proxy-info  # early stop on proxy error
cmsrel CMSSW_15_0_10
cd CMSSW_15_0_10/src
cmsenv

rm -rf PhysicsTools/NanoTuples
git clone https://github.com/hypnotismer/NanoTuples PhysicsTools/NanoTuples -b nanov15-finetune-hgluglu
#PhysicsTools/NanoTuples/scripts/install_onnxruntime.sh
#wget https://coli.web.cern.ch/coli/tmp/.231117-195737_ak15_stage2/model.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak15/V02/model.onnx
scram b -j$(cat /proc/cpuinfo | grep MHz | wc -l)

cd ../../tmp
workdir=`pwd`
path="$workdir/$filename"
cd ..
cd CMSSW_15_0_10/src

cmsDriver.py step2  \
    -s NANO --process NANO --data  \
    --nThreads ${NTHREAD} \
    --eventcontent NANOAOD --datatier NANOAOD \
    -n ${NEVENT} \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
    --conditions auto:run2_data \
    --filein file:${FILEIN} \
    --fileout file:${path}

xrdcp --silent -p -f ${path} ${FILEOUT}