# Gate C Runbook: Integration Checks

## Objective
Validate rosbag adapter roundtrip and primitive index/search integration under deterministic fixtures.
Validate maximalization M1 runtime-style callback path checks.

## Commands
1. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5`

## Expected Outputs
- `robot_rosbag_roundtrip.json`
- `robot_primitive_search_eval.json`
- Integration status details in `integration_readiness_contract.json`
- Max-wave callback/runtime evidence in `max_resource_validation_log.md`

## Fail Signatures
- Roundtrip hash mismatch.
- Primitive search P@10 < 0.90.
- Missing schema/version metadata.
- M1 live-callback simulation parity failure.

## Rollback
- Patch integration adapter/indexing logic.
- Rerun Gate C and all downstream gates.
