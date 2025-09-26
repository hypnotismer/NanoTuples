#!/bin/bash

NEVENT="$1"
NTHREAD="$2"
FILEIN="$3"
FILEOUT="$4"

cmsDriver.py step2 \
    -s NANO --process NANO --mc \
    --nThreads ${NTHREAD} \
    --eventcontent NANOAODSIM --datatier NANOAODSIM \
    -n ${NEVENT} \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
    --conditions auto:phase1_2018_realistic \
    --filein file:${FILEIN}  \
    --fileout file:${FILEOUT}