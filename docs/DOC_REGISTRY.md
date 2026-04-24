<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Documentation Registry

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This is the canonical registry for the repo documentation surface. Paths are
repo-relative. `status=current` means the doc is part of the active authority
or support surface. `status=historical` means lineage only.

<p>
  <img src="../.github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

## Front Door And Root Policy

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `README.md` | front door | current | `proofs/ENGINEERING_BLOCKERS.md` | blocker or release-surface change |
| `CHANGELOG.md` | release change log | current | `pyproject.toml` | version or docs release change |
| `CONTRIBUTING.md` | contributor policy | current | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | setup, test, or scope-rule change |
| `SECURITY.md` | security policy | current | `LICENSE` | security contact or process change |
| `CODE_OF_CONDUCT.md` | community conduct policy | current | self | conduct policy change |
| `GOVERNANCE.md` | claim and authority policy | current | `proofs/ENGINEERING_BLOCKERS.md` | authority semantics change |
| `RELEASING.md` | release gate policy | current | `proofs/ENGINEERING_BLOCKERS.md` | release gate or publish-path change |

## Docs Directory Surface

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `docs/README.md` | docs index | current | `README.md` | doc topology change |
| `docs/ARCHITECTURE.md` | runtime and package map | current | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | runtime or package-surface change |
| `docs/AUDITOR_PLAYBOOK.md` | audit route | current | `proofs/ENGINEERING_BLOCKERS.md` | verify-command or authority change |
| `docs/FAQ.md` | blocker and acquisition FAQ | current | `proofs/ENGINEERING_BLOCKERS.md` | blocker or acquisition-surface change |
| `docs/CLAIM_BOUNDARY.md` | active narrowed claim boundary | current | `proofs/narrow_claim/NARROW_CLAIM_GATE.json` | claim-boundary change |
| `docs/MECHANICS_LAYER.md` | mechanics-layer audit for current claim | current | `proofs/narrow_claim/NARROW_CLAIM_GATE.json` | mechanics-boundary change |
| `docs/SUPPORT.md` | support routing | current | `SECURITY.md` | support-route change |
| `docs/LEGAL_BOUNDARIES.md` | legal and visibility notes | current | `LICENSE` | claim, license, or visibility change |
| `docs/OPERATOR_RUNBOOK.md` | CLI/operator surface | current | `src/zpe_robotics/cli.py` | CLI surface change |
| `docs/PUBLIC_AUDIT_LIMITS.md` | audit boundary | current | `proofs/ENGINEERING_BLOCKERS.md` | claim-boundary change |
| `docs/RELEASE_CANDIDATE.md` | staged release note | current | `proofs/ENGINEERING_BLOCKERS.md` | package or blocker-state change |
| `docs/family/ROBOTICS_RELEASE_LINKAGE.md` | IMC linkage boundary | current | `proofs/imc_audit/imc_architecture_audit.json` | IMC linkage interpretation change |
| `docs/ZPBOT_V2_AUTHORITY_SURFACE.md` | packet-contract reference | current | `src/zpe_robotics/wire.py` | packet-contract change |

## Proof, Runbook, And Historical Surface

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `proofs/ENGINEERING_BLOCKERS.md` | governing blocker proof | current | self | new benchmark, red-team, or integration result |
| `proofs/narrow_claim/NARROW_CLAIM_GATE.json` | selected narrow-claim gate | current | self | claim-boundary change |
| `proofs/narrow_claim/NARROW_CLAIM_RATIFICATION.md` | narrow-claim rationale | current | `proofs/narrow_claim/NARROW_CLAIM_GATE.json` | claim-boundary change |
| `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | package/runtime boundary | current | self | packaging or runtime boundary change |
| `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md` | publisher setup runbook | current | `.github/workflows/publish.yml` | publish workflow or PyPI UI path change |
| `proofs/FINAL_STATUS.md` | supporting status note | supporting | `proofs/ENGINEERING_BLOCKERS.md` | current authority reroute |
| `proofs/artifacts/historical/README.md` | historical index | historical | self | preservation policy change |

## Metadata

| Path | Role | Status | Authority | Update trigger |
|---|---|---|---|---|
| `CITATION.cff` | citation metadata | current | `pyproject.toml` | version or package identity change |
| `LICENSE` | legal text | current | self | license text change |
