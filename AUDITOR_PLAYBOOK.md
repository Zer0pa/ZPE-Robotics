# Auditor Playbook

This is the shortest honest verification path for the current private staged
Robotics repo.

It is intentionally narrow. This repo has not yet completed Phase 5
blind-clone verification, so this playbook is a repo-local verification guide,
not a public release claim.

## Current Truth

- the current release-candidate kernel gate is `GO`
- hosted `M1` is closed by GitHub Actions run `23200176105`
- hosted `E-G3` is closed by GitHub Actions run `23202700744`
- hosted `IT-03` + `IT-05` are closed by GitHub Actions run `23202700741`
- hosted `IT-04` is closed by GitHub Actions run `23202700798`
- historical February bundles are preserved for lineage only
- blind-clone verification is still a follow-on task

## Shortest Repo-Local Verify Path

1. Create an environment and install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,netnew]"
```

2. Run the lightweight test surface:

```bash
python -m pytest tests -q
```

3. Verify the release-candidate CLI surface:

```bash
python -m zpe_robotics.cli verify proofs/release_candidate/canonical_release_packet.zpbot
python -m zpe_robotics.cli info proofs/release_candidate/canonical_release_packet.zpbot
```

4. If clean-clone or blind-clone staging is promoted, run the repo-local max-wave path:

```bash
python scripts/run_wave1.py \
  --output-root proofs/reruns/robotics_wave1_local \
  --seed 20260220 \
  --determinism-runs 5 \
  --max-wave
```

5. Validate the rerun bundle:

```bash
python scripts/validate_net_new.py --artifacts proofs/reruns/robotics_wave1_local
python scripts/regression_pack.py --artifacts proofs/reruns/robotics_wave1_local
```

## Compare Against

- `proofs/logs/PRE_REPO_AUTHORITY_SNAPSHOT_2026-03-09.md`
- `proofs/FINAL_STATUS.md`
- `proofs/CONSOLIDATED_PROOF_REPORT.md`

## If Your Replay Disagrees

Capture:

- commit SHA
- exact commands
- stdout and stderr
- the produced rerun directory

Do not convert disagreement into a pass narrative. Record the mismatch.
