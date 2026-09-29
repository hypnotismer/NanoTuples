# 2024 MiniAOD submission

`request_run.py` prepares full NanoAOD HTCondor jobs using the current NanoTuples checkout. `request_run_slim.py` selects the corresponding slimmed workflow. It creates one job per input MiniAOD file, a source snapshot, a JDL, and log paths. The default action is preparation only; add `--submit` to call `condor_submit` after the preflight checks.

Use Python 3 in the CMSSW_15_0_10 area. The worker creates the same CMSSW release, builds the snapshot, runs the 2024 data or MC NanoAOD configuration, and copies each output to EOS with `xrdcp`. The submitter chooses one of `run-mc-2024.sh`, `run-mc-2024-slim.sh`, `run-data-2024.sh`, or `run-data-2024-slim.sh`; each sets its own conditions and customise function. The four scripts share CMSSW setup in `run_nano.sh`. The snapshot includes locally available model files, including ignored `.onnx` files, so the job does not depend on a remote Git branch.

## Inputs

Choose exactly one input source:

- `--dataset /primary/campaign/MINIAODSIM` for a 2024 MC DAS dataset, or a 2024 `MINIAOD` dataset with `--mode data`. Use `--dbs-instance prod/phys03` for samples not in `prod/global`.
- `--input-list files.txt` with one `/store/...` LFN, `root://...` URL, or absolute EOS file path per line. Empty lines and `#` comments are allowed.
- One or more `--input-file` arguments with those same file formats.

An AFS symlink into EOS is accepted as an EOS file path. Other local files cannot be accessed by generic batch workers.

Output goes to IHEP CCEOS. `request_run.py` sets only `OUTPUT_ROOT` (`root://cceos.ihep.ac.cn:1094//store/user/zkou`). The rest of the path is `CustomizedNanoAOD` or `CustomizedNanoAOD-slim`, then `V0/{year}/{MC|Data}/{dataset}/{prepid}/`. The output file keeps the input name, with `MiniAODv6` replaced by `CustomizedNanoAODv15`. For a sample listed under `samples/<dataset>/<prepid>/`, those directory names are used. The JDL proxy is `submit/x509up`, created by `submit/x509up-gen` when it is missing or shorter than the 192-hour proxy.

```bash
cd "$CMSSW_BASE/src/PhysicsTools/NanoTuples"
submit/x509up-gen
python3 submit/request_run.py \
  --mode mc \
  --input-list /path/to/miniaod_files.txt \
  --events 100 --threads 4 --max-files 2
```

Choose the submission script to select full or slimmed output:

```bash
# Full customized NanoAOD: run-mc-2024.sh or run-data-2024.sh
python3 submit/request_run.py --year 2024 --mode mc \
  --dataset /primary/campaign/MINIAODSIM

# Slimmed NanoAOD: run-mc-2024-slim.sh or run-data-2024-slim.sh
python3 submit/request_run_slim.py --year 2024 --mode mc \
  --dataset /primary/campaign/MINIAODSIM
```

`request_run.py --output-kind slim` is equivalent to `request_run_slim.py`. The slim
worker makes the full NanoAOD in Condor scratch, then runs the CMSSW-bundled
NanoAODTools PostProcessor and sends only the skimmed ROOT file to EOS. It
uses the old VH/VX 0L, 1L, and 2L event selection with Run 3 electron MVA IDs:
0L requires no loose electrons or muons and PFMET > 100 GeV; 1L requires exactly
one tight electron or one tight muon; 2L requires at least two loose electrons
or at least two loose muons. Every selected event also needs an AK15 Puppi jet
with two subjets. The 2L condition follows the old same-flavor logic; an e-mu
pair alone does not pass. `keep_and_drop_2024.txt` copies the old branch drop
rules. `Runs` and `LuminosityBlocks` remain, with their original pre-skim MC
normalization metadata.

The printed `nano.jdl` path can be reviewed and submitted with `condor_submit <path>`. To prepare and submit in one command, add `--submit`. Optional settings include `--name`, `--job-dir`, `--memory-mb`, `--max-runtime`, `--scram-arch`, and `--requirements`. Without `--events`, each job processes its entire file. Generated job directories live under `submit/jobs/` by default and are ignored by Git.

The current tagger configuration requires the configured AK15 xggg preprocessing JSON and ONNX model, plus the standard AK8 ONNX model. `--submit` checks for them. DAS planning uses the same `submit/x509up` proxy. If the tagger paths change, update the checks in `request_run.py` and `run_nano.sh` to match the cff configuration.

## 2024 background MC manifest and DAS scan

The 2024 background MC samples are listed under
`samples/<datasetname>/<prepid>/`. Each directory contains the exact `dataset` path,
its `dbs_instance` (`prod/global` or `prod/phys03`), and an
`expected_summary.json` with the DAS file and event counts. The directory name
uses the `prep_id` returned by DAS. The DY `PTLL-40to100` 1J and 2J samples
remain in `prod/phys03`; the DY `PTLL-100`, `200`, `400`, and `600` samples
are inclusive in LHE jet multiplicity and published in `prod/global`. Include
the instance in DAS queries.

Run `python3 python/scan_datasets.py --workers 4` from the NanoTuples checkout
to scan every listed dataset. The scanner writes the legacy-compatible JSON
`filelist` containing each file LFN and event count, plus `scan.json` with
aggregate counts. It compares those counts against `expected_summary.json` and
can resume after interruption. Use `--only <datasetname>` for one sample and
`--force` to refresh an existing result. Scanning queries DAS; it does not
submit Condor jobs. The legacy `xsdb` and `xs` files are cross-section data
from XSDB, independent of the DAS file-list scan. The `filelist` stores only
`name` and `nevents` for each file to keep AFS use small; it has the same
JSON structure consumed by the old `python/sample.py`. The DAS scan does not
produce `xsdb` or choose an `xs` entry. These need an authenticated XSDB
query and cross-section review before they are written.
