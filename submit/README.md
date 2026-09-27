# 2024 MiniAOD submission

`request_run.py` prepares full NanoAOD HTCondor jobs using the current NanoTuples checkout. `request_run_slim.py` selects the corresponding slimmed workflow. It creates one job per input MiniAOD file, a source snapshot, a JDL, and log paths. The default action is preparation only; add `--submit` to call `condor_submit` after the preflight checks.

Use Python 3 in the CMSSW_15_0_10 area. The worker creates the same CMSSW release, builds the snapshot, runs the 2024 data or MC NanoAOD configuration, and copies each output to EOS with `xrdcp`. The submitter chooses one of `run-mc-2024.sh`, `run-mc-2024-slim.sh`, `run-data-2024.sh`, or `run-data-2024-slim.sh`; each sets its own conditions and customise function. The four scripts share CMSSW setup in `run_nano.sh`. The snapshot includes locally available model files, including ignored `.onnx` files, so the job does not depend on a remote Git branch.

## Inputs

Choose exactly one input source:

- `--dataset /primary/campaign/MINIAODSIM` for a 2024 MC DAS dataset, or a 2024 `MINIAOD` dataset with `--mode data`. Use `--dbs-instance prod/phys03` for samples not in `prod/global`.
- `--input-list files.txt` with one `/store/...` LFN, `root://...` URL, or absolute EOS file path per line. Empty lines and `#` comments are allowed.
- One or more `--input-file` arguments with those same file formats.

An AFS symlink into EOS is accepted as an EOS file path. Other local files cannot be accessed by generic batch workers. The output directory must be an EOS path (including an AFS symlink into EOS) or a `root://` URL.

```bash
cd "$CMSSW_BASE/src/PhysicsTools/NanoTuples"
python3 submit/request_run.py \
  --mode mc \
  --input-list /path/to/miniaod_files.txt \
  --output-dir /eos/user/u/username/nanotuples_2024 \
  --events 100 --threads 4 --max-files 2
```

Choose the submission script to select the output:

```bash
# Full customized NanoAOD: run-mc-2024.sh or run-data-2024.sh
python3 submit/request_run.py --year 2024 --mode mc \
  --dataset /primary/campaign/MINIAODSIM --output-dir /eos/user/u/username/nanotuples_2024

# Slimmed NanoAOD: run-mc-2024-slim.sh or run-data-2024-slim.sh
python3 submit/request_run_slim.py --year 2024 --mode mc \
  --dataset /primary/campaign/MINIAODSIM --output-dir /eos/user/u/username/nanotuples_2024
```

`request_run.py --output-kind slim` is equivalent to `request_run_slim.py`. The slim
worker makes the full NanoAOD in Condor scratch, then runs the CMSSW-bundled
NanoAODTools PostProcessor and sends only the skimmed ROOT file to EOS. It
uses the old VH/VX 0L, 1L, and 2L event selection with Run 3 electron MVA IDs:
0L requires no loose electrons or muons and MET > 100 GeV; 1L requires exactly
one tight electron or one tight muon; 2L requires at least two loose electrons
or at least two loose muons. Every selected event also needs an AK15 Puppi jet
with two subjets. The 2L condition follows the old same-flavor logic; an e-mu
pair alone does not pass. `keep_and_drop_2024.txt` copies the old branch drop
rules. `Runs` and `LuminosityBlocks` remain, with their original pre-skim MC
normalization metadata. Output names end in `_nano.root` or `_nano_slim.root`.

The printed `nano.jdl` path can be reviewed and submitted with `condor_submit <path>`. To prepare and submit in one command, add `--submit`. Optional settings include `--name`, `--job-dir`, `--memory-mb`, `--max-runtime`, `--scram-arch`, `--proxy`, and `--requirements`. Without `--events`, each job processes its entire file. Generated job directories live under `submit/jobs/` by default and are ignored by Git.

The current tagger configuration requires the configured AK15 xggg preprocessing JSON and ONNX model, plus the standard AK8 ONNX model. `--submit` checks for them and requires a grid proxy with at least one hour remaining. DAS planning also needs a valid proxy. A prepared JDL still needs those files and a valid proxy before direct `condor_submit` succeeds. If the tagger paths change, update the checks in `request_run.py` and `run_nano.sh` to match the cff configuration.

## 2024 background MC manifest and DAS scan

The 2024 background MC samples from AN-24-106 are listed under
`samples/<datasetname>/<prepid>/`. Each directory contains the exact `dataset` path,
its `dbs_instance` (`prod/global` or `prod/phys03`), and an
`expected_summary.json` with the DAS file and event counts. The directory name
uses the `prep_id` returned by DAS. Some DY samples are published in
`prod/phys03`, so the instance must be included in DAS queries.

Run `python3 submit/scan_datasets.py --workers 4` from the NanoTuples checkout
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
