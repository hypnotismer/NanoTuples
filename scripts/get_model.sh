#!/bin/bash

# Model paths to download
models=(
    "InclParticleTransformer-MD/ak8/V01/model.onnx"                     # GloParT v1
    "InclParticleTransformer-MD/ak8/V02-HidLayer/model_embed.onnx"      # GloParT v2 (exposing hidden-layer)
    "InclParticleTransformer-MD/ak8/V03/model.onnx"                     # GloParT v3 (the cmssw version)
    "InclParticleTransformer-MD/ak8/V03FullScore/model_full_score.onnx" # GloParT v3 (the full-score version, w/ hidden layer)
    "InclParticleTransformer-MD/ak15/V02/model.onnx"                    # GloParT v2 for AK15 jets
)

for path in "${models[@]}"; do
  wget "https://coli.web.cern.ch/coli/repo/NanoTuples_data/$path" -O "$CMSSW_BASE/src/PhysicsTools/NanoTuples/data/$path" --quiet --show-progress
done