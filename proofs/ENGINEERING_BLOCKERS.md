# Engineering Blockers

Date: 2026-04-24
Phase: Post-Phase-10 authority reconciliation

## Governing Verdict

Engineering is not complete.

The selected PRD execution gate is the narrow-claim gate. That gate passes only
for the bounded-lossy archive/search surface recorded in
`proofs/narrow_claim/NARROW_CLAIM_GATE.json`; it is not a completion
certificate.

The decisive evidence is:

- benchmark gates: `B1=PASS`, `B2=PASS`, `B3=FAIL`, `B4=PASS`, `B5=PASS`
- red-team: attacks `1`, `2`, `5`, and `6` withstand; attack `4` partially withstands; attack `3` fails; attack `7` remains open
- IMC integration: `zpe-robotics` still does not route `.zpbot` encode or decode through the current ZPE-IMC Rust surface

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

## Resolved Since Phase 9

### Red-Team Attack 5 False-Positive Rate

Evidence:

- `proofs/red_team/red_team_report.json`
- `proofs/release_candidate/anomaly_detection_result.json`
- `proofs/release_candidate/anomaly_threshold_sweep.json`

Current truth:

- the active detector threshold is `3.22`
- the red-team attack-5 artifact records `0 / 20 = 0.0` false positives
- the Phase 10 holdout artifact records `false_positive_rate=0.05` on `100` nominal samples with `recall=0.9` on `10` anomalous samples
- the selected threshold is corpus-bound to `phase10-file-level-histogram-holdout-v1`

Boundary:

- this resolves the blocker-facing attack `5` false-positive row on the declared surface
- this does not close `B3`, attack `3`, attack `7`, or the missing Robotics Rust ABI
- this does not authorize a general anomaly-readiness claim beyond the declared threshold-selected holdout surface

## Ratified Narrow Claim

Evidence:

- `proofs/narrow_claim/NARROW_CLAIM_GATE.json`
- `proofs/narrow_claim/NARROW_CLAIM_RATIFICATION.md`
- `docs/CLAIM_BOUNDARY.md`
- `docs/MECHANICS_LAYER.md`

Current truth:

- the bounded-lossy archive/search gate is ratified for the current public
  surface
- the gate depends on decoded PrimitiveIndex search, not search without decode
- the gate preserves `B3`, attack `3`, attack `7`, attack `4` limits, and the
  missing Robotics Rust ABI as unresolved

What this does not close:

- full engineering completion
- bit-exact replay
- lossless qualification
- live robot control
- ZPE-IMC runtime routing
- external third-party reproduction

## Non-Blocking But Still Open

- Trusted Publishing workflow alignment is fixed in `.github/workflows/publish.yml`, but the PyPI UI registration step in `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md` is still operator-only.
- External third-party reproduction remains open by design and is recorded as such in `proofs/red_team/red_team_report.json`.
- The available real dataset for attack 4 is better than the synthetic corpus but still undershoots the 200-episode and 50 Hz target, so corpus-strength claims remain bounded.
