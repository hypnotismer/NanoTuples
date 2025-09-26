#!/bin/bash

NEVENT="$1"
NTHREAD="$2"
FILEIN="$3"
FILEOUT="$4"

cmsDriver.py step2  \
    -s NANO --process NANO --data  \
    --nThreads ${NTHREAD} \
    --eventcontent NANOAOD --datatier NANOAOD \
    -n ${NEVENT} \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
    --conditions auto:run2_data \
    --filein file:${FILEIN}  \
    --fileout file:${FILEOUT}