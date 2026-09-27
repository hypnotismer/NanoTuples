#!/usr/bin/env python3
"""Skim a Run 3 customized NanoAOD with the Run 2 VH/VX 0L/1L/2L logic."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

ROOT.PyConfig.IgnoreCommandLineOptions = True

BRANCH_RULES = Path(__file__).with_name("keep_and_drop_2024.txt")
REQUIRED_BRANCHES = (
    "nElectron", "Electron_pt", "Electron_eta", "Electron_mvaIso_WP90",
    "Electron_mvaIso_WP80", "nMuon", "Muon_pt", "Muon_eta",
    "Muon_looseId", "Muon_tightId", "Muon_pfRelIso04_all", "Muon_dxy",
    "Muon_dz", "nAK15Puppi", "AK15Puppi_subJetIdx1",
    "AK15Puppi_subJetIdx2", "MET_pt",
)


class VHSkim2024(Module):
    """Match the old VVVProducer cuts, using Run 3 electron MVA branch names."""

    def analyze(self, event):
        electrons = Collection(event, "Electron")
        loose_e = sum(
            electron.pt > 20 and abs(electron.eta) < 2.5 and electron.mvaIso_WP90
            for electron in electrons
        )
        tight_e = sum(
            electron.pt > 30 and abs(electron.eta) < 2.5 and electron.mvaIso_WP80
            for electron in electrons
        )
        muons = Collection(event, "Muon")
        loose_mu = sum(
            muon.pt > 20 and abs(muon.eta) < 2.4 and muon.looseId
            and muon.pfRelIso04_all < 0.25
            for muon in muons
        )
        tight_mu = sum(
            muon.pt > 25 and abs(muon.eta) < 2.4 and muon.tightId
            and muon.pfRelIso04_all < 0.06 and abs(muon.dxy) < 0.05
            and abs(muon.dz) < 0.2
            for muon in muons
        )
        has_fatjet = any(
            jet.subJetIdx1 >= 0 and jet.subJetIdx2 >= 0
            for jet in Collection(event, "AK15Puppi")
        )
        if not has_fatjet:
            return False
        pass_0l = loose_e == 0 and loose_mu == 0 and event.MET_pt > 100
        pass_1l = tight_e == 1 or tight_mu == 1
        pass_2l = loose_e >= 2 or loose_mu >= 2
        return pass_0l or pass_1l or pass_2l


def event_count(path: Path, check_schema: bool = False) -> int:
    root_file = ROOT.TFile.Open(str(path), "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Cannot open NanoAOD: {path}")
    try:
        events = root_file.Get("Events")
        if not events or not events.InheritsFrom("TTree"):
            raise RuntimeError(f"NanoAOD has no Events tree: {path}")
        if check_schema:
            available = {branch.GetName() for branch in events.GetListOfBranches()}
            missing = set(REQUIRED_BRANCHES) - available
            if missing:
                raise RuntimeError("Missing Run 3 skim branches: " + ", ".join(sorted(missing)))
        return events.GetEntries()
    finally:
        root_file.Close()


def slim(input_path: Path, output_path: Path) -> tuple[int, int]:
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output must be different files")
    if not BRANCH_RULES.is_file():
        raise FileNotFoundError(BRANCH_RULES)
    total = event_count(input_path, check_schema=True)
    temporary = Path(tempfile.mkdtemp(prefix="nano_slim_", dir=output_path.parent))
    try:
        processor = PostProcessor(
            str(temporary), [str(input_path)], modules=[VHSkim2024()],
            provenance=True, outputbranchsel=str(BRANCH_RULES), postfix="",
        )
        processor.run()
        produced = temporary / input_path.name
        if not produced.is_file():
            raise RuntimeError(f"PostProcessor did not produce {produced}")
        passed = event_count(produced)
        produced.replace(output_path)
    finally:
        shutil.rmtree(temporary)
    return total, passed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="full customized NanoAOD ROOT file")
    parser.add_argument("output", type=Path, help="slimmed NanoAOD ROOT file")
    args = parser.parse_args()
    total, passed = slim(args.input, args.output)
    print(f"Slimmed NanoAOD: kept {passed}/{total} Events in {args.output}", flush=True)


if __name__ == "__main__":
    main()
