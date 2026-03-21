<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Public Audit Limits

<p>
  <img src=".github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

This repo is a private staging repo with a public package acquisition surface.
It is not a public release-ready robotics platform.

What this repo can honestly establish today:

- the current standalone package identity and install surface
- the March 21 blocker-state authority files
- the real-data benchmark result where `B1`, `B2`, `B4`, and `B5` pass
- the current release workflow boundary and operator-only PyPI UI step
- preserved historical proof lineage under `proofs/artifacts/historical/`

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

| Limit | Current state | Why it matters |
|---|---|---|
| Engineering completion | not complete | `B3` fails and red-team attacks `3` and `5` fail |
| Replay claim | not bit-exact | strict `np.array_equal` is false on the current `.zpbot` round-trip |
| Real-corpus strength | bounded | the real dataset run used `136` episodes at `10 Hz`, below the `200` episode / `50 Hz` target |
| Rust integration | not present | `current_python_calls_rust=false` in the IMC architecture audit |
| External reproduction | open | current evidence remains first-party |
| Historical proof bundles | lineage only | preserved for provenance, not current authority |
| Public release | not authorized | the repo remains private staging only |

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

This repo cannot honestly establish today:

- full engineering completion
- a public-release verdict
- strict bit-exact replay on the governing benchmark surface
- anomaly false-positive rate at or below `0.05`
- current Rust routing through ZPE-IMC for the robotics `.zpbot` path
- independent third-party reproduction

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

Use these files together:

- `README.md`
- `AUDITOR_PLAYBOOK.md`
- `proofs/ENGINEERING_BLOCKERS.md`
- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/red_team/red_team_report.json`
- `proofs/artifacts/historical/README.md`
