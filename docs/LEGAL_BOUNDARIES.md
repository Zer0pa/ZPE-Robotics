<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Legal Boundaries

This note is a release-surface summary only. `../LICENSE` at the repo root is
the legal source of truth for Zer0pa Source-Available License v7.0.

<p>
  <img src="../.github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

| Boundary | Current truth | What it does not mean |
|---|---|---|
| license | Zer0pa Source-Available License v7.0; `../LICENSE` is the legal source of truth | support docs and README tables are summaries, not legal overrides |
| source visibility | public GitHub repo | public visibility is not engineering completion or release readiness |
| public acquisition | package acquisition exists via `pip install zpe-robotics` | package availability does not erase blocker-state failures |
| claim boundary | engineering is not complete; `B3` fails, red-team attack `3` fails, external reproduction is open, and IMC Rust routing is missing | no `GO` verdict exists for a release-ready robotics surface |
| runtime boundary | no IMC runtime import or robotics `.zpbot` Rust ABI is present today | current docs linkage to IMC is not runtime coupling |
| proof boundary | historical bundles remain lineage only | historical bundles do not outrank current blocker files |

- Mixed evidence does not become a pass.
- Package availability does not equal a release-ready engineering verdict.
- Use `../proofs/ENGINEERING_BLOCKERS.md`,
  `../proofs/enterprise_benchmark/GATE_VERDICTS.json`, and
  `../proofs/red_team/red_team_report.json`, and
  `../proofs/release_candidate/anomaly_reconciliation_result.json` as the
  current authority surface.

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

Use these files together when the boundary matters:

- `../LICENSE`
- `../README.md`
- `PUBLIC_AUDIT_LIMITS.md`
- `../proofs/ENGINEERING_BLOCKERS.md`
- `../proofs/release_candidate/anomaly_reconciliation_result.json`
- `../proofs/imc_audit/imc_architecture_audit.json`
