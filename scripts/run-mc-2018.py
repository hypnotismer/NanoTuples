# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: --mc -n 100 --nThreads 8 --python_filename run-mc-2018.py --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --scenario pp --era Run2_2018 --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC --filein root://cms-xrd-global.cern.ch//store/data/Run2018A/SingleMuon/MINIAOD/UL2018_MiniAODv2_GT36-v2/60000/7A01165C-3168-BF47-AFA5-9FAC3D3BA209.root --fileout file:/afs/cern.ch/user/z/zkou/eos/hgg/test/finetune_11.root --customise_commands process.source.duplicateCheckMode = cms.untracked.string("noDuplicateCheck"); process.pvbsTable.src = cms.InputTag("offlineSlimmedPrimaryVertices"); import FWCore.ParameterSet.Config as cms; (hasattr(process,"finalTaus") and setattr(process.finalTaus,"cut", cms.string("pt > 18 && abs(eta)<2.3"))) or True; (hasattr(process,"finalBoostedTaus") and setattr(process.finalBoostedTaus,"cut", cms.string("pt > 150 && abs(eta)<2.3"))) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"boostedTauMCTable") and process.nanoTableTask.remove(process.boostedTauMCTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"boostedTauTable") and process.nanoTableTask.remove(process.boostedTauTable)) or True; (hasattr(process,"jetPuppiTable") and hasattr(process.jetPuppiTable,"variables") and hasattr(process.jetPuppiTable.variables,"puIdDisc") and delattr(process.jetPuppiTable.variables,"puIdDisc")) or True; (hasattr(process,"jetPuppiTable") and hasattr(process.jetPuppiTable,"variables") and hasattr(process.jetPuppiTable.variables,"puId") and delattr(process.jetPuppiTable.variables,"puId")) or True; (hasattr(process,"nanoSequenceMC") and hasattr(process,"tauTimeLifeInfos") and process.nanoSequenceMC.remove(process.tauTimeLifeInfos)) or True; (hasattr(process,"nanoSequence") and hasattr(process,"tauTimeLifeInfos") and process.nanoSequence.remove(process.tauTimeLifeInfos)) or True; (hasattr(process,"nanoTask") and hasattr(process,"tauTimeLifeInfos") and process.nanoTask.remove(process.tauTimeLifeInfos)) or True; (hasattr(process,"nanoTablesTask") and hasattr(process,"tauTimeLifeInfoTable") and process.nanoTablesTask.remove(process.tauTimeLifeInfoTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"tauTimeLifeInfoTable") and process.nanoTableTask.remove(process.tauTimeLifeInfoTable)) or True; (hasattr(process,"tauTimeLifeInfos") and delattr(process,"tauTimeLifeInfos")) or True; (hasattr(process,"tauTimeLifeInfoTable") and delattr(process,"tauTimeLifeInfoTable")) or True; (hasattr(process,"electronTimeLifeInfos") and hasattr(process.electronTimeLifeInfos,"primaryVertices") and setattr(process.electronTimeLifeInfos,"primaryVertices", cms.InputTag("offlineSlimmedPrimaryVertices"))) or True; (hasattr(process,"nanoSequenceMC") and hasattr(process,"electronTimeLifeInfos") and process.nanoSequenceMC.remove(process.electronTimeLifeInfos)) or True; (hasattr(process,"nanoSequence") and hasattr(process,"electronTimeLifeInfos") and process.nanoSequence.remove(process.electronTimeLifeInfos)) or True; (hasattr(process,"nanoTask") and hasattr(process,"electronTimeLifeInfos") and process.nanoTask.remove(process.electronTimeLifeInfos)) or True; (hasattr(process,"nanoTablesTask") and hasattr(process,"electronTimeLifeInfoTable") and process.nanoTablesTask.remove(process.electronTimeLifeInfoTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"electronTimeLifeInfoTable") and process.nanoTableTask.remove(process.electronTimeLifeInfoTable)) or True; (hasattr(process,"electronTimeLifeInfos") and delattr(process,"electronTimeLifeInfos")) or True; (hasattr(process,"electronTimeLifeInfoTable") and delattr(process,"electronTimeLifeInfoTable")) or True; (hasattr(process,"muonTimeLifeInfos") and hasattr(process.muonTimeLifeInfos,"primaryVertices") and setattr(process.muonTimeLifeInfos,"primaryVertices", cms.InputTag("offlineSlimmedPrimaryVertices"))) or True; (hasattr(process,"nanoSequenceMC") and hasattr(process,"muonTimeLifeInfos") and process.nanoSequenceMC.remove(process.muonTimeLifeInfos)) or True; (hasattr(process,"nanoSequence") and hasattr(process,"muonTimeLifeInfos") and process.nanoSequence.remove(process.muonTimeLifeInfos)) or True; (hasattr(process,"nanoTask") and hasattr(process,"muonTimeLifeInfos") and process.nanoTask.remove(process.muonTimeLifeInfos)) or True; (hasattr(process,"nanoTablesTask") and hasattr(process,"muonTimeLifeInfoTable") and process.nanoTablesTask.remove(process.muonTimeLifeInfoTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"muonTimeLifeInfoTable") and process.nanoTableTask.remove(process.muonTimeLifeInfoTable)) or True; (hasattr(process,"muonTimeLifeInfos") and delattr(process,"muonTimeLifeInfos")) or True; (hasattr(process,"muonTimeLifeInfoTable") and delattr(process,"muonTimeLifeInfoTable")) or True
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018

process = cms.Process('NANO',Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('root://cms-xrd-global.cern.ch//store/data/Run2018A/SingleMuon/MINIAOD/UL2018_MiniAODv2_GT36-v2/60000/7A01165C-3168-BF47-AFA5-9FAC3D3BA209.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('--mc nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:/afs/cern.ch/user/z/zkou/eos/hgg/test/finetune_11.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v16_L1v1', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads = 8
process.options.numberOfStreams = 0

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoTuples.nanoTuples_cff
from PhysicsTools.NanoTuples.nanoTuples_cff import nanoTuples_customizeMC 

#call to customisation function nanoTuples_customizeMC imported from PhysicsTools.NanoTuples.nanoTuples_cff
process = nanoTuples_customizeMC(process)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon 

#call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeCommon(process)

# End of customisation functions


# Customisation from command line

process.source.duplicateCheckMode = cms.untracked.string("noDuplicateCheck"); process.pvbsTable.src = cms.InputTag("offlineSlimmedPrimaryVertices"); import FWCore.ParameterSet.Config as cms; (hasattr(process,"finalTaus") and setattr(process.finalTaus,"cut", cms.string("pt > 18 && abs(eta)<2.3"))) or True; (hasattr(process,"finalBoostedTaus") and setattr(process.finalBoostedTaus,"cut", cms.string("pt > 150 && abs(eta)<2.3"))) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"boostedTauMCTable") and process.nanoTableTask.remove(process.boostedTauMCTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"boostedTauTable") and process.nanoTableTask.remove(process.boostedTauTable)) or True; (hasattr(process,"jetPuppiTable") and hasattr(process.jetPuppiTable,"variables") and hasattr(process.jetPuppiTable.variables,"puIdDisc") and delattr(process.jetPuppiTable.variables,"puIdDisc")) or True; (hasattr(process,"jetPuppiTable") and hasattr(process.jetPuppiTable,"variables") and hasattr(process.jetPuppiTable.variables,"puId") and delattr(process.jetPuppiTable.variables,"puId")) or True; (hasattr(process,"nanoSequenceMC") and hasattr(process,"tauTimeLifeInfos") and process.nanoSequenceMC.remove(process.tauTimeLifeInfos)) or True; (hasattr(process,"nanoSequence") and hasattr(process,"tauTimeLifeInfos") and process.nanoSequence.remove(process.tauTimeLifeInfos)) or True; (hasattr(process,"nanoTask") and hasattr(process,"tauTimeLifeInfos") and process.nanoTask.remove(process.tauTimeLifeInfos)) or True; (hasattr(process,"nanoTablesTask") and hasattr(process,"tauTimeLifeInfoTable") and process.nanoTablesTask.remove(process.tauTimeLifeInfoTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"tauTimeLifeInfoTable") and process.nanoTableTask.remove(process.tauTimeLifeInfoTable)) or True; (hasattr(process,"tauTimeLifeInfos") and delattr(process,"tauTimeLifeInfos")) or True; (hasattr(process,"tauTimeLifeInfoTable") and delattr(process,"tauTimeLifeInfoTable")) or True; (hasattr(process,"electronTimeLifeInfos") and hasattr(process.electronTimeLifeInfos,"primaryVertices") and setattr(process.electronTimeLifeInfos,"primaryVertices", cms.InputTag("offlineSlimmedPrimaryVertices"))) or True; (hasattr(process,"nanoSequenceMC") and hasattr(process,"electronTimeLifeInfos") and process.nanoSequenceMC.remove(process.electronTimeLifeInfos)) or True; (hasattr(process,"nanoSequence") and hasattr(process,"electronTimeLifeInfos") and process.nanoSequence.remove(process.electronTimeLifeInfos)) or True; (hasattr(process,"nanoTask") and hasattr(process,"electronTimeLifeInfos") and process.nanoTask.remove(process.electronTimeLifeInfos)) or True; (hasattr(process,"nanoTablesTask") and hasattr(process,"electronTimeLifeInfoTable") and process.nanoTablesTask.remove(process.electronTimeLifeInfoTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"electronTimeLifeInfoTable") and process.nanoTableTask.remove(process.electronTimeLifeInfoTable)) or True; (hasattr(process,"electronTimeLifeInfos") and delattr(process,"electronTimeLifeInfos")) or True; (hasattr(process,"electronTimeLifeInfoTable") and delattr(process,"electronTimeLifeInfoTable")) or True; (hasattr(process,"muonTimeLifeInfos") and hasattr(process.muonTimeLifeInfos,"primaryVertices") and setattr(process.muonTimeLifeInfos,"primaryVertices", cms.InputTag("offlineSlimmedPrimaryVertices"))) or True; (hasattr(process,"nanoSequenceMC") and hasattr(process,"muonTimeLifeInfos") and process.nanoSequenceMC.remove(process.muonTimeLifeInfos)) or True; (hasattr(process,"nanoSequence") and hasattr(process,"muonTimeLifeInfos") and process.nanoSequence.remove(process.muonTimeLifeInfos)) or True; (hasattr(process,"nanoTask") and hasattr(process,"muonTimeLifeInfos") and process.nanoTask.remove(process.muonTimeLifeInfos)) or True; (hasattr(process,"nanoTablesTask") and hasattr(process,"muonTimeLifeInfoTable") and process.nanoTablesTask.remove(process.muonTimeLifeInfoTable)) or True; (hasattr(process,"nanoTableTask") and hasattr(process,"muonTimeLifeInfoTable") and process.nanoTableTask.remove(process.muonTimeLifeInfoTable)) or True; (hasattr(process,"muonTimeLifeInfos") and delattr(process,"muonTimeLifeInfos")) or True; (hasattr(process,"muonTimeLifeInfoTable") and delattr(process,"muonTimeLifeInfoTable")) or True 
process.source.delayReadingEventProducts = cms.untracked.bool(False)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
