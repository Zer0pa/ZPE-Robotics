# Engineering Blockers

Date: 2026-03-21
Phase: 9 -- Enterprise Benchmark, IMC Integration, Technical Closure

## Governing Verdict

Engineering is not complete.

The decisive evidence is:

- benchmark gates: `B1=PASS`, `B2=PASS`, `B3=FAIL`, `B4=PASS`, `B5=PASS`
- red-team: attacks `1`, `2`, `5`, and `6` withstand; attack `4` partially withstands; attack `3` fails; attack `7` remains open
- IMC integration: `zpe-robotics` still does not route `.zpbot` encode or decode through the current ZPE-IMC Rust surface

## 2026-04-24 Reconciliation Note

Attack `5` was rerun on fresh `origin/main` commit `7b7921eacd8d` using the
current detector threshold surface. The empirical result reproduced the
committed red-team report: `false_positives=0`, `nominal_trajectories_tested=20`,
`false_positive_rate=0.0`, `z_threshold_used=3.22`, verdict `WITHSTANDS`.
The blocker text below has been reconciled to that evidence rather than the
older failed reading.

## Blocking Items

### 1. IMC Rust Integration Is Still Missing

Evidence:

- `proofs/imc_audit/imc_architecture_audit.json`

Current truth:

- `current_python_calls_rust` is `false`
- the available ZPE-IMC PyO3 surface is multimodal, not a robotics `.zpbot` encode/decode ABI

What is needed to close it:

- add or expose a real robotics encode/decode ABI in ZPE-IMC
- route `zpe-robotics` through that Rust path
- prove the routed path in tests and cross-platform CI

### 2. Benchmark Gate B3 Failed

Evidence:

- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/enterprise_benchmark/benchmark_result.json`

Current truth:

- `zpe_p8` is searchable without decode
- `zpe_p8` is not bit-exact on raw float32 replay
- the fixed gate requires both

What is needed to close it:

- either make the codec bit-exact on the governing replay surface
- or explicitly ratify a different acceptance gate in a new phase instead of narrating this one green

### 3. Red-Team Attack 3 Failed

Evidence:

- `proofs/red_team/red_team_report.json`

Current truth:

- strict `np.array_equal` is `false` for the core `.zpbot` round-trip
- strict `np.array_equal` is also `false` for the LeRobot wrapper round-trip

What is needed to close it:

- remove any bit-exact or lossless wording from the active claim surface
- or change the codec path so the strict replay requirement actually holds

## Non-Blocking But Still Open

- Trusted Publishing workflow alignment is fixed in `.github/workflows/publish.yml`, but the PyPI UI registration step in `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md` is still operator-only.
- External third-party reproduction remains open by design and is recorded as such in `proofs/red_team/red_team_report.json`.
- The available real dataset for attack 4 is better than the synthetic corpus but still undershoots the 200-episode and 50 Hz target, so corpus-strength claims remain bounded.
