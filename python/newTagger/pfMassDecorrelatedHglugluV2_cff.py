import FWCore.ParameterSet.Config as cms

# use CustomDeepBoostedJetTagInfoProducer (to include recovered 4-vector)
from PhysicsTools.NanoTuples.pfParticleTransformerAK8TagInfos_cfi import pfParticleTransformerAK8TagInfos as pfParticleTransformerV2JetTagInfos
from RecoBTag.ONNXRuntime.boostedJetONNXJetTagsProducer_cfi import boostedJetONNXJetTagsProducer
from PhysicsTools.NanoTuples.newTagger.pfMassDecorrelatedHglugluV2DiscriminatorsJetTags_cfi import pfMassDecorrelatedHglugluV2DiscriminatorsJetTags

pfMassDecorrelatedHglugluV2TagInfos = pfParticleTransformerV2JetTagInfos.clone(
    use_puppiP4 = False,
    jet_radius = 1.5,
)

pfMassDecorrelatedHglugluV2JetTags = boostedJetONNXJetTagsProducer.clone(
    src = 'pfMassDecorrelatedHglugluV2TagInfos',
    preprocess_json = 'PhysicsTools/NanoTuples/data/Hgluglu-finetune/ak15/V02/preprocess.json',
    model_path = 'PhysicsTools/NanoTuples/data/Hgluglu-finetune/ak15/V02/model.onnx',
    flav_names = [
        "probHgg", "probTTbarTop", "probTTbarQCD", "probWJetsQCD", # 4 cls
    ], 
    debugMode = False,
)

# declare all the discriminators
# probs
_pfMassDecorrelatedHglugluV2JetTagsProbs = ['pfMassDecorrelatedHglugluV2JetTags:' + flav_name
                                 for flav_name in pfMassDecorrelatedHglugluV2JetTags.flav_names]
# meta-taggers
_pfMassDecorrelatedHglugluV2JetTagsMetaDiscrs = ['pfMassDecorrelatedHglugluV2DiscriminatorsJetTags:' + disc.name.value()
                                      for disc in pfMassDecorrelatedHglugluV2DiscriminatorsJetTags.discriminators]

_pfMassDecorrelatedHglugluV2JetTagsAll = _pfMassDecorrelatedHglugluV2JetTagsProbs + _pfMassDecorrelatedHglugluV2JetTagsMetaDiscrs
#_pfMassDecorrelatedHglugluV2JetTagsAll = _pfMassDecorrelatedHglugluV2JetTagsProbs
