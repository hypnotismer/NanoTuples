# Xggg fine-tuned AK15 model

The JSON files are copied from the CMSSW_10_6_31 xggg tagger as an interface reference. The old Run 2 ONNX model is not included.

Place the validated Run 3 export at `model.onnx` in this directory. Check that its input tensors agree with `preprocess_corr.json` and that its six outputs match the names in `python/newTagger/pfMassDecorrelatedXgggFinetuneV2_cff.py`. Update the preprocessing JSON if the Run 3 model uses a different feature layout.
