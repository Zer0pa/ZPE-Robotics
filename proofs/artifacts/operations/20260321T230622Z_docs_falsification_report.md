# Docs Falsification Report

Timestamp: 2026-03-21T23:06:22Z
Repo: ./zpe-robotics

## Unsupported Claims Removed Or Downgraded
- README wording was tightened from a broader "public wedge" framing to a narrower "current release surface" framing.
- README package-status language was reduced from "current public PyPI package" to "current installable package artifact".
- FAQ wording now states that package availability does not change blocker status and reframes PyPI divergence as release-metadata drift, not release readiness.

## Path And Render Issues Found
- `docs/ZPBOT_V2_AUTHORITY_SURFACE.md` lacked the shared masthead and section-bar framing used across the repo docs family.
- `OPERATOR_RUNBOOK.md` scanned as a numbered list rather than a fast lookup table.
- `docs/DOC_REGISTRY.md` was too wide for clean GitHub/mobile scanning.
- current runbooks and the E-G3 workflow still hardcoded stale dated rerun roots.
- `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` still used machine-absolute `/Users/...` anchors.

## Resolutions Applied
- added the shared masthead and section-bar system to the ZPBOT authority doc and thin root surfaces that lacked family framing
- converted key routing/command sections to compact lookup tables
- split the doc registry into smaller grouped tables
- rewired live runbooks, scripts, and the E-G3 workflow away from stale dated rerun roots
- removed the untracked March 16 rerun folders after cutting live references
- replaced absolute release-surface anchors with repo-relative paths

## Remaining Owner Inputs
- PyPI Trusted Publishing UI registration remains operator-only
- engineering blockers remain owner-visible and unresolved in `proofs/ENGINEERING_BLOCKERS.md`

## Live-Vs-Local Drift
- local drift found: current docs and workflow still contained stale rerun-root references from older execution surfaces
- resolved locally in this pass
- remote GitHub drift is resolved only once this commit is pushed
