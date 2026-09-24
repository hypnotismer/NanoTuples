# 2024 MiniAOD submission

`request_run.py` prepares HTCondor jobs using the current NanoTuples checkout. It creates one job per input MiniAOD file, a source snapshot, a JDL, and log paths. The default action is preparation only; add `--submit` to call `condor_submit` after the preflight checks.

Use Python 3 in the CMSSW_15_0_10 area. The worker creates the same CMSSW release, builds the snapshot, runs the 2024 data or MC NanoAOD configuration, and copies each output to EOS with `xrdcp`. The snapshot includes locally available model files, including ignored `.onnx` files, so the job does not depend on a remote Git branch.

## Inputs

Choose exactly one input source:

- `--dataset /primary/campaign/MINIAODSIM` for a 2024 MC DAS dataset, or a 2024 `MINIAOD` dataset with `--mode data`.
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

The printed `nano.jdl` path can be reviewed and submitted with `condor_submit <path>`. To prepare and submit in one command, add `--submit`. Optional settings include `--name`, `--job-dir`, `--memory-mb`, `--max-runtime`, `--scram-arch`, `--proxy`, and `--requirements`. Without `--events`, each job processes its entire file. Generated job directories live under `submit/jobs/` by default and are ignored by Git.

The current tagger configuration requires the configured AK15 xggg preprocessing JSON and ONNX model, plus the standard AK8 ONNX model. `--submit` checks for them and requires a grid proxy with at least one hour remaining. DAS planning also needs a valid proxy. A prepared JDL still needs those files and a valid proxy before direct `condor_submit` succeeds. If the tagger paths change, update the checks in `request_run.py` and `run_nano.sh` to match the cff configuration.
