<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Public Audit Limits

<p>
  <img src="../.github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

This repo is public and the package acquisition surface is public.
Those visibility facts do not amount to engineering completion or a
release-ready robotics verdict.

What this repo can honestly establish today:

- the current standalone package identity and install surface
- the current public GitHub repo and PyPI acquisition surfaces
- the bounded-lossy archive/search gate ratified in `proofs/narrow_claim/NARROW_CLAIM_GATE.json`
- the March 21 blocker-state authority files
- the real-data benchmark result where `B1`, `B2`, `B4`, and `B5` pass
- the Phase 10 attack-5 threshold evidence on the declared holdout surface
- the current release workflow boundary and operator-only PyPI UI step
- preserved historical proof lineage under `proofs/artifacts/historical/`

<p>
  <img src="../.github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

| Limit | Current state | Why it matters |
|---|---|---|
| Repo visibility | public GitHub repo | visibility is not an engineering pass |
| Package availability | public on PyPI | installation does not imply release readiness |
| Narrow claim gate | bounded-lossy archive/search passes | this is not full engineering completion |
| Engineering completion | not complete | `B3` fails, red-team attack `3` fails, attack `7` is open, and Robotics Rust routing is absent |
| Replay claim | not bit-exact | strict `np.array_equal` is false on the current `.zpbot` round-trip |
| Anomaly claim | threshold-selected only | attack `5` withstands at threshold `3.22` on the declared Phase 10 holdout surface, not as a general anomaly-readiness claim |
| Real-corpus strength | bounded | the real dataset run used `136` episodes at `10 Hz`, below the `200` episode / `50 Hz` target |
| Rust integration | not present | `current_python_calls_rust=false` in the IMC architecture audit |
| External reproduction | open | current evidence remains first-party |
| Historical proof bundles | lineage only | preserved for provenance, not current authority |
| Release-ready verdict | not authorized | public visibility does not erase blocker-state failures |

<p>
  <img src="../.github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

This repo cannot honestly establish today:

- full engineering completion
- a release-ready robotics verdict
- strict bit-exact replay on the governing benchmark surface
- general anomaly false-positive behavior outside the declared Phase 10 holdout surface
- current Rust routing through ZPE-IMC for the robotics `.zpbot` path
- independent third-party reproduction

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

Use these files together:

- `../README.md`
- `AUDITOR_PLAYBOOK.md`
- `../LICENSE`
- `../proofs/ENGINEERING_BLOCKERS.md`
- `../proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `../proofs/red_team/red_team_report.json`
- `../proofs/artifacts/historical/README.md`
