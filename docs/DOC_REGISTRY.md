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

| path | class | audience | status | source of truth | related docs | update trigger | render notes |
|---|---|---|---|---|---|---|---|
| `README.md` | front-door | all | current | `proofs/ENGINEERING_BLOCKERS.md` | `docs/README.md`; `RELEASING.md` | blocker or release-surface change | root |
| `CHANGELOG.md` | release | contributor | current | `pyproject.toml` | `RELEASING.md`; `README.md` | version or docs release change | root |
| `CONTRIBUTING.md` | policy | contributor | current | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | `SECURITY.md`; `docs/SUPPORT.md` | setup, test, or scope-rule change | root |
| `SECURITY.md` | policy | contributor | current | `LICENSE` | `docs/SUPPORT.md`; `RELEASING.md` | security contact or process change | root |
| `GOVERNANCE.md` | policy | maintainer | current | `proofs/ENGINEERING_BLOCKERS.md` | `README.md`; `RELEASING.md` | authority semantics change | root |
| `RELEASING.md` | release | maintainer | current | `proofs/ENGINEERING_BLOCKERS.md` | `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md`; `README.md` | release gate or publish-path change | root |
| `RELEASE_CANDIDATE.md` | release | all | current | `proofs/ENGINEERING_BLOCKERS.md` | `README.md`; `RELEASING.md` | package or blocker-state change | root |
| `AUDITOR_PLAYBOOK.md` | audit | auditor | current | `proofs/ENGINEERING_BLOCKERS.md` | `PUBLIC_AUDIT_LIMITS.md`; `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | verify-command or authority change | root |
| `PUBLIC_AUDIT_LIMITS.md` | audit | all | current | `proofs/ENGINEERING_BLOCKERS.md` | `AUDITOR_PLAYBOOK.md`; `docs/LEGAL_BOUNDARIES.md` | claim-boundary change | root |
| `OPERATOR_RUNBOOK.md` | operator | operator | current | `src/zpe_robotics/cli.py` | `README.md`; `docs/SUPPORT.md` | CLI surface change | none |
| `docs/README.md` | index | all | current | `README.md` | `DOC_REGISTRY.md`; `SUPPORT.md` | doc topology change | docs |
| `docs/ARCHITECTURE.md` | technical | contributor | current | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | `ZPBOT_V2_AUTHORITY_SURFACE.md`; `README.md` | runtime or package-surface change | docs |
| `docs/FAQ.md` | support | all | current | `proofs/ENGINEERING_BLOCKERS.md` | `SUPPORT.md`; `README.md` | blocker or acquisition-surface change | docs |
| `docs/SUPPORT.md` | support | all | current | `SECURITY.md` | `FAQ.md`; `../proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md` | support-route change | docs |
| `docs/LEGAL_BOUNDARIES.md` | legal | all | current | `LICENSE` | `PUBLIC_AUDIT_LIMITS.md`; `README.md` | claim, license, or visibility change | docs |
| `docs/family/ROBOTICS_RELEASE_LINKAGE.md` | family | maintainer | current | `proofs/imc_audit/imc_architecture_audit.json` | `../ARCHITECTURE.md`; `../../GOVERNANCE.md` | IMC linkage interpretation change | family |
| `docs/ZPBOT_V2_AUTHORITY_SURFACE.md` | contract | maintainer | current | `src/zpe_robotics/wire.py` | `ARCHITECTURE.md`; `RELEASE_CANDIDATE.md` | packet-contract change | none |
| `proofs/ENGINEERING_BLOCKERS.md` | proof | auditor | current | self | `README.md`; `RELEASING.md` | new benchmark, red-team, or integration result | none |
| `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | proof | maintainer | current | self | `README.md`; `docs/ARCHITECTURE.md` | packaging or runtime boundary change | none |
| `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md` | runbook | operator | current | `.github/workflows/publish.yml` | `RELEASING.md`; `docs/SUPPORT.md` | publish workflow or PyPI UI path change | none |
| `proofs/FINAL_STATUS.md` | proof | auditor | supporting | `proofs/ENGINEERING_BLOCKERS.md` | `README.md`; `proofs/artifacts/historical/README.md` | current authority reroute | none |
| `proofs/artifacts/historical/README.md` | historical | auditor | historical | self | `proofs/FINAL_STATUS.md`; `README.md` | preservation policy change | none |
| `CITATION.cff` | citation | researcher | current | `pyproject.toml` | `README.md`; `LICENSE` | version or package identity change | none |
| `LICENSE` | legal | all | current | self | `CITATION.cff`; `docs/LEGAL_BOUNDARIES.md` | license text change | none |
