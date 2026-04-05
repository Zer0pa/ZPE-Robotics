<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Release Candidate

<p>
  <img src="../.github/assets/readme/section-bars/release-notes.svg" alt="RELEASE NOTES" width="100%">
</p>

This document records the March 18, 2026 release-candidate surface for
`zpe-robotics 0.1.0`. It is not the governing March 21 engineering
authority. Use `../proofs/ENGINEERING_BLOCKERS.md` for the current completion
boundary.

<p>
  <img src="../.github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

| Surface | Release-candidate fact | Current caveat |
|---|---|---|
| Package | `zpe-robotics 0.1.0` package artifact exists | current repo authority remains blocker-state, not release-candidate prose |
| Synthetic fixture compression | `238.02421307506054x` | the real-data benchmark later recorded `187.1345x` |
| CLI surface | `zpe` ships encode, decode, verify, info, search, anomaly, LeRobot, token export, and audit-bundle commands | availability does not imply all claims are fully closed |
| Searchability | primitive search works without decode on the benchmark surface | `B3` still fails because strict bit-exact replay is not proven |
| Publishing | package upload path exists | Trusted Publishing UI registration is still operator-only |

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Claim surface | Evidence | Caveat |
|---|---|---|
| canonical reference packet SHA | `../proofs/red_team/red_team_report.json` attack `6` | Python 3.12 parity held for the reference packet, but strict raw-array equality still fails on the current round-trip path |
| real-data compression | `../proofs/enterprise_benchmark/benchmark_result.json`, `../proofs/enterprise_benchmark/GATE_VERDICTS.json` | benchmark gates `B1`, `B2`, `B4`, and `B5` pass; `B3` fails |
| hostile-path auditability | packet verification and audit-bundle surfaces in `../src/zpe_robotics/` and `../tests/` | auditability does not imply public-release readiness |
| build/install truth | `../proofs/artifacts/operations/20260321T203557Z_technical_alignment_verification.md` | technical release-surface alignment is green, but engineering completion is not |

<p>
  <img src="../.github/assets/readme/section-bars/downstream-action-items.svg" alt="DOWNSTREAM ACTION ITEMS" width="100%">
</p>

This release-candidate note does not claim:

- strict bit-exact replay on the governing benchmark surface
- anomaly false-positive rate at or below `0.05`
- current Rust routing through ZPE-IMC for robotics `.zpbot`
- full robotics-platform release readiness
- public-release authorization

Use these files when you need the current state instead of the March 18 note:

- `../proofs/ENGINEERING_BLOCKERS.md`
- `../proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `../proofs/red_team/red_team_report.json`
- `../RELEASING.md`
