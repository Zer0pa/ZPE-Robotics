# Docs Falsification Report

Timestamp: 2026-03-21T22:01:22Z
Repo: /Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics
Gate: docs-owner release-surface truth alignment

## Verification Performed

- ran `python -m pytest tests/test_release_surface.py tests/test_cli.py -q`
  and got `10 passed`
- built the package in a temporary venv with `python -m build`
- verified Markdown links across the updated docs surface
- verified imported image asset paths across the updated GitHub-facing docs
- ran an adversarial docs review against the current blocker, benchmark,
  red-team, IMC audit, and release-surface artifacts

## Unsupported Claims Removed Or Downgraded

- removed stale repo-wide `GO`, clean-clone-forward, and no-blocker language
  from the front-door docs
- removed bit-perfect and bit-stable replay wording from the active
  release-candidate surface
- made the blocker-state authority explicit in `README.md`,
  `AUDITOR_PLAYBOOK.md`, `PUBLIC_AUDIT_LIMITS.md`, `GOVERNANCE.md`, and
  `RELEASING.md`
- downgraded `proofs/FINAL_STATUS.md` to a historical pointer instead of a
  governing current-status surface

## Path And Render Issues Found

- root and `docs/*` surfaces were missing the imported shared asset scaffold;
  fixed by copying `.github/assets/readme/`
- `docs/README.md` previously routed to a missing support doc; fixed by adding
  `docs/SUPPORT.md`
- internal Markdown links and image paths in the reviewed docs now resolve
  repo-locally

## Remaining Owner Inputs

- PyPI Trusted Publishing still needs the operator-only UI registration step in
  `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md`
- a future package release is still required if the public PyPI project
  description is to reflect the March 21 blocker-state docs surface

## Live-vs-Local Drift Found And Resolved

- repo-local front-door docs previously drifted from the March 21 blocker-state;
  they now defer consistently to `proofs/ENGINEERING_BLOCKERS.md`
- historical release-candidate notes previously read as current authority;
  they now point back to the blocker-state and historical lineage boundary
- public package metadata on PyPI still reflects the March 18 release surface;
  that drift remains visible and is not narrated away

## Verdict

The docs pass is technically coherent and truth-bounded. The repo's engineering
release gate remains blocked by `B3`, red-team attacks `3` and `5`, and the
absence of a robotics `.zpbot` Rust ABI.
