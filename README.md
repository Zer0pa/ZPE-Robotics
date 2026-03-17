# ZPE-Robotics

ZPE-Robotics is the Robotics sector private staging repo for the Wave-1
deterministic robotics codec, proof corpus, and repo-formation work.

This repo is staged privately. It is not a public release surface and it
has not yet passed Phase 5 blind-clone verification.

## Current Status

| Surface | Current truth |
|---|---|
| Visibility | private staging only |
| Repo state | inner repo normalized on 2026-03-09 |
| Current technical verdict | `GO` for the 2026-03-17 release-candidate kernel gate |
| Active blockers | none on the current release-candidate gate |
| Hosted runtime closure | `M1` closed on 2026-03-17 via GitHub Actions run `23200176105` |
| Hosted comparator closure | `E-G3` closed on 2026-03-17 via GitHub Actions run `23202700744` |
| Hosted composition closure | `IT-03` + `IT-05` closed on 2026-03-17 via GitHub Actions run `23202700741` |
| Hosted parity matrix | `IT-04` closed on 2026-03-17 via GitHub Actions run `23202700798` |
| Historical bundles | included under `proofs/artifacts/historical/` |
| Portable repo-root rerun | not yet performed |

## What This Repo Contains

- `src/zpe_robotics/`: Wave-1 package code
- `tests/`: sector tests
- `scripts/`: execution and validation scripts
- `docs/`: front-door, architecture, legal-boundary, and linkage docs
- `proofs/`: historical bundles, current status docs, logs, and runbooks

## What This Repo Does Not Claim

- It does not claim launch readiness.
- It does not claim that the current private staged tree has been verified
  from a clean clone.
- It does not treat the February historical bundles as current authority.
- It does not claim that blind-clone verification or public release staging
  are complete today.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,netnew]"
python -m pytest tests -q
```

Optional repo-local follow-on verify path when clean-clone staging opens:

```bash
python scripts/run_wave1.py \
  --output-root proofs/reruns/robotics_wave1_local \
  --seed 20260220 \
  --determinism-runs 5 \
  --max-wave
```

## Where To Read First

- `proofs/FINAL_STATUS.md`
- `proofs/logs/PRE_REPO_AUTHORITY_SNAPSHOT_2026-03-09.md`
- `AUDITOR_PLAYBOOK.md`
- `PUBLIC_AUDIT_LIMITS.md`
- `docs/README.md`

## Honesty Rules

- Runtime and artifact truth outrank prose.
- Historical artifacts remain historical even when they contain stronger
  older claims than the current rerun.
- Mixed evidence is not a pass.
- `GO` here means the release-candidate kernel gate passed, not that public
  launch or blind-clone staging are complete.
