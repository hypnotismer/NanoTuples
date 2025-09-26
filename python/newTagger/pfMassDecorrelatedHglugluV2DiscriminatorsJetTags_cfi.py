import FWCore.ParameterSet.Config as cms

pfMassDecorrelatedHglugluV2DiscriminatorsJetTags = cms.EDProducer(
   'BTagProbabilityToDiscriminator',
   discriminators = cms.VPSet(
      cms.PSet(
         name = cms.string('probHggvsQCD'),
         numerator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probHgg'),
            ),
         denominator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probTTbarQCD'),
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probWJetsQCD'),
            ),
         ),
      cms.PSet(
         name = cms.string('probHggvsTopQCD'),
         numerator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probHgg'),

            ),
         denominator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probTTbarQCD'),
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probWJetsQCD'),
            cms.InputTag('pfMassDecorrelatedDeepHggV3JetTags', 'probTTbarTop'),
            ),
         ),
      )
   )
