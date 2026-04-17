<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Documentation Registry

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This is the canonical registry for the repo documentation surface. Paths are
repo-relative. `status=current` means the doc is part of the active authority
or support surface. `status=supporting` means useful but non-governing context.
`status=historical` means lineage only.

<p>
  <img src="../.github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

## Front Door And Root Surface

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `README.md` | front door | current | `proofs/ENGINEERING_BLOCKERS.md` | blocker or release-surface change |
| `CHANGELOG.md` | release change log | current | `pyproject.toml` | version or docs release change |
| `LICENSE` | legal text | current | self | license text change |

## Docs Directory Surface

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `docs/README.md` | docs index | current | `README.md` | doc topology change |
| `docs/ARCHITECTURE.md` | runtime and package map | current | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | runtime or package-surface change |
| `docs/AUDITOR_PLAYBOOK.md` | audit route | current | `proofs/ENGINEERING_BLOCKERS.md` | verify-command or authority change |
| `docs/DOC_REGISTRY.md` | documentation registry | current | self | doc topology or authority-source change |
| `docs/FAQ.md` | blocker and acquisition FAQ | current | `proofs/ENGINEERING_BLOCKERS.md` | blocker or acquisition-surface change |
| `docs/SUPPORT.md` | support routing | current | `README.md` | support-route or contact change |
| `docs/LEGAL_BOUNDARIES.md` | legal and visibility notes | current | `LICENSE` | claim, license, or visibility change |
| `docs/OPERATOR_RUNBOOK.md` | CLI/operator surface | current | `src/zpe_robotics/cli.py` | CLI surface change |
| `docs/PUBLIC_AUDIT_LIMITS.md` | audit boundary | current | `proofs/ENGINEERING_BLOCKERS.md` | claim-boundary change |
| `docs/RELEASE_CANDIDATE.md` | March 18 snapshot note | supporting | `proofs/ENGINEERING_BLOCKERS.md` | package or blocker-state change |
| `docs/family/ROBOTICS_RELEASE_LINKAGE.md` | IMC linkage boundary | current | `proofs/imc_audit/imc_architecture_audit.json` | IMC linkage interpretation change |
| `docs/market_surface.json` | structured market-facing summary | current | `README.md` | front-door summary or buyer framing change |
| `docs/ZPBOT_V2_AUTHORITY_SURFACE.md` | packet-contract reference | current | `src/zpe_robotics/wire.py` | packet-contract change |

## Proof, Runbook, And Historical Surface

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `proofs/ENGINEERING_BLOCKERS.md` | governing blocker proof | current | self | new benchmark, red-team, or integration result |
| `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | package/runtime boundary | current | self | packaging or runtime boundary change |
| `proofs/FINAL_STATUS.md` | supporting status note | supporting | `proofs/ENGINEERING_BLOCKERS.md` | current authority reroute |
| `proofs/artifacts/historical/README.md` | historical index | historical | self | preservation policy change |

## Reorientation Artifacts

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `docs/_reorientation/2026-04-17/NOVELTY_CARD.md` | per-product novelty input for license drafting | current | `src/zpe_robotics/`, `README.md` | novelty framing or product surface change |
| `docs/_reorientation/2026-04-17/FIX_LOG.md` | audit log for the 2026-04-17 reorientation pass | current | repo doc surface | reorientation edits change |
| `docs/_reorientation/2026-04-17/OPEN_QUESTIONS.md` | unresolved licensing or framing questions | current | repo doc surface | unresolved question is closed or added |
