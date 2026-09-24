import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoTuples.pfParticleTransformerAK8TagInfos_cfi import pfParticleTransformerAK8TagInfos as pfParticleTransformerV2JetTagInfos
from RecoBTag.ONNXRuntime.boostedJetONNXJetTagsProducer_cfi import boostedJetONNXJetTagsProducer

pfMassDecorrelatedXgggFinetuneV2TagInfos = pfParticleTransformerV2JetTagInfos.clone(
    use_puppiP4 = False,
    jet_radius = 1.5,
)

# Replace model.onnx with the Run 3 fine-tuned export before running inference.
pfMassDecorrelatedXgggFinetuneV2JetTags = boostedJetONNXJetTagsProducer.clone(
    src = 'pfMassDecorrelatedXgggFinetuneV2TagInfos',
    preprocess_json = 'PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak15/V02_xggg_finetune/preprocess_corr.json',
    model_path = 'PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak15/V02_xggg_finetune/model.onnx',
    flav_names = [
        'probXggg', 'probLeak', 'probTop', 'probQCD',
        'resonanceMassCorr', 'visiableMassCorr',
    ],
    debugMode = False,
)

_pfMassDecorrelatedXgggFinetuneV2JetTagsProbs = ['pfMassDecorrelatedXgggFinetuneV2JetTags:' + flav_name
                                 for flav_name in pfMassDecorrelatedXgggFinetuneV2JetTags.flav_names]
