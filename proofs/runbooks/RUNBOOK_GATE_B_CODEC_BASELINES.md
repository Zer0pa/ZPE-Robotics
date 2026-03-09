# Gate B Runbook: Core Codec and Baselines

## Objective
Implement `.zpbot` codec, benchmark harness, fidelity metrics, and baseline comparators.

## Planned Modules
- `src/zpe_robotics/codec.py`
- `src/zpe_robotics/fixtures.py`
- `src/zpe_robotics/kinematics.py`
- `src/zpe_robotics/primitives.py`
- `src/zpe_robotics/anomaly.py`
- `src/zpe_robotics/rosbag_adapter.py`
- `src/zpe_robotics/vla_eval.py`

## Commands
1. `python -m pytest -q`
2. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5`
3. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5 --max-wave --skip-net-new`

## Expected Outputs
- Core benchmark/fidelity artifact JSONs generated with threshold checks.
- No uncaught exceptions in nominal path.

## Falsification Focus
- Attempt threshold breaches by adversarial spikes and discontinuities before claim promotion.

## Fail Signatures
- Compression ratio below thresholds.
- RMSE threshold breaches.
- Token baseline non-improvement.
- High-frequency fidelity kill test failure (D5.3).

## Rollback
- Patch affected algorithm module only.
- Re-execute Gate B and downstream gates.
