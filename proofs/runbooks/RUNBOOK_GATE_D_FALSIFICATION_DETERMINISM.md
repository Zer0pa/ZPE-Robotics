# Gate D Runbook: Falsification and Determinism

## Objective
Execute malformed/adversarial campaigns with zero uncaught crashes and confirm 5/5 determinism.

## Campaigns
- DT-ROB-1 malformed URDF/joint-state stream handling
- DT-ROB-2 adversarial spikes/discontinuities
- DT-ROB-3 rosbag corruption/reorder contamination
- DT-ROB-4 deterministic replay on mixed corpora
- DT-ROB-5 primitive confusion stress
- DT-ROB-MAX-1 playback jitter/reorder kill test
- DT-ROB-MAX-2 confusable motif primitive kill test
- DT-ROB-MAX-3 high-frequency control trace fidelity kill test

## Commands
1. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5`
2. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local_replay --seed 20260220 --determinism-runs 5`

## Expected Outputs
- `falsification_results.md`
- `determinism_replay_results.json`
- `regression_results.txt`

## Fail Signatures
- Any uncaught exception during campaigns.
- Determinism hash inconsistency.
- Regression mismatch after fixes.

## Rollback
- Patch fault handling paths.
- Rerun Gate D and Gate E.
