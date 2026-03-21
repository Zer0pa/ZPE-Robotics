# Root Surface Verification

Timestamp: 2026-03-21T23:28:32Z
Repo: /Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics
Branch: main

## Objective
- make the repo root the single branded main surface locally and on GitHub
- remove stray helper docs from the root and place them under `docs/`

## Root After Cleanup
- `CHANGELOG.md`
- `CITATION.cff`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `docs/`
- `GOVERNANCE.md`
- `LICENSE`
- `Makefile`
- `proofs/`
- `pyproject.toml`
- `README.md`
- `RELEASING.md`
- `scripts/`
- `SECURITY.md`
- `src/`
- `tests/`
- `uv.lock`

## Structural Changes
- moved `AUDITOR_PLAYBOOK.md` to `docs/AUDITOR_PLAYBOOK.md`
- moved `PUBLIC_AUDIT_LIMITS.md` to `docs/PUBLIC_AUDIT_LIMITS.md`
- moved `OPERATOR_RUNBOOK.md` to `docs/OPERATOR_RUNBOOK.md`
- moved `RELEASE_CANDIDATE.md` to `docs/RELEASE_CANDIDATE.md`
- deleted duplicate root `SUPPORT.md`
- updated root README, docs index, docs registry, publish workflow, audit-bundle defaults, and COMM-03 provenance to the new doc locations
- removed local top-level junk: `.DS_Store`, `.pytest_cache/`, `dist/`, `.venv/`

## Verification
- `python -m pytest tests/test_release_surface.py tests/test_cli.py tests/test_audit_bundle.py -q`
  - result: `13 passed in 0.24s`
- moved-doc asset and markdown-target check
  - result: `ok moved-doc paths`
- publish workflow YAML parse
  - result: `ok publish yaml parse`
- repo root listing rechecked after cleanup

## Verdict
- PASS for the root-surface cleanliness gate
- engineering blocker-state remains unchanged and still lives under `proofs/ENGINEERING_BLOCKERS.md`

