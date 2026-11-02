# 2024 MiniAOD submission

Create each sample by hand under `samples/<datasetname>/<prepid>/`. Put its input path in a file named `dataset`. For central samples, that path is the full DAS dataset; `request_run.py` queries `prod/global`. For signal, put the XRootD directory containing its MiniAOD ROOT files in `dataset`.

```bash
cd "$CMSSW_BASE/src/PhysicsTools/NanoTuples"
mkdir -p samples/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/GEN-RunIII2024Summer24MiniAODv6-00002
printf '%s\n' '/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v3/MINIAODSIM' > samples/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/GEN-RunIII2024Summer24MiniAODv6-00002/dataset
```

The signal `dataset` file can instead contain a full XRootD directory URL, for example `root://cceos.ihep.ac.cn:1094//store/user/zkou/MiniAODstore/V0/2024/MC/WZR_012j_NLO_WToLNu_ZRTo3Glu_M-100_13p6TeV-pythia8`. The sample name and prep id come from the two directories under `samples/`, not from the XRootD path. `PrivateMiniAOD-V0-2024` is a local label for this example, not an McM prep id. A central `MINIAOD` dataset is data; other datasets are MC.

From `submit/`, pass the two directory names to the generator. These examples put one file in each JDL; remove `--max-files 1` to queue the full sample:

```bash
cd "$CMSSW_BASE/src/PhysicsTools/NanoTuples/submit"
./x509up-gen
# Signal
python3 request_run.py WZR_012j_NLO_WToLNu_ZRTo3Glu_M-100_13p6TeV-pythia8 PrivateMiniAOD-V0-2024 --max-files 1
# Background MC
python3 request_run.py TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8 GEN-RunIII2024Summer24MiniAODv6-00002 --max-files 1
# 2024 data
python3 request_run.py JetMET0 Run2024C-MINIv6NANOv15-v1 --max-files 1
```

For 2024 data, `samples/` contains the `MINIv6NANOv15` C-I datasets for JetMET0/1, EGamma0/1, and Muon0/1. Review a generated JDL under `submit/jdl/` and submit it with `condor_submit jdl/<datasetname>_<prepid>.jdl`.

Use `request_run_slim.py` with the same two names for slim output. `--nolog` gives every file the Run 2 `overwritten` log names; the default keeps separate logs. `--events` and `--max-files` are optional. The JDL uses 8 CPUs and 4096 MB of memory, as in Run 2. The runtime limit is four hours.

When `samples/<datasetname>/<prepid>/filelist` exists, the generator reuses it. Otherwise it queries DAS or lists the signal XRootD directory and writes `filelist` in the same format as Run 2. It writes one JDL per sample under `submit/jdl/` and logs under `submit/log/<datasetname>/<prepid>/`; it does not submit automatically. The proxy comes from `submit/x509up-gen` and is referenced in the JDL as `submit/x509up`.

The worker creates CMSSW_15_0_10, clones `hypnotismer/NanoTuples` branch `nanov15-finetune-xggg`, downloads the AK15 xggg and AK8 ONNX models, builds, runs, and copies the output to IHEP EOS. The slim worker uses `python/slim_nano.py` from that GitHub branch, so push selection changes there before submitting slim jobs.

## Sample scans

A sample directory needs `dataset` and, after scanning, `filelist`. The submission generator reads an existing `filelist` or scans the path in `dataset` and saves one. Central DAS queries use `prod/global`; when DAS does not provide a file's event count, the generator reads the ROOT `Events` tree. Signal XRootD paths use `xrdfs` to list files and read each ROOT `Events` tree. During ROOT counting it prints each file path and its event count. A JDL is written only after every input file has an event count.

To prefill missing file lists for all samples, run `python3 python/scan_datasets.py --workers 4` from the NanoTuples checkout. `--only <datasetname>` limits it to one sample name, and `--force` refreshes an existing `filelist`. This command does not create JDLs or submit jobs. The older `expected_summary.json`, `scan.json`, and `dbs_instance` files are no longer used.
