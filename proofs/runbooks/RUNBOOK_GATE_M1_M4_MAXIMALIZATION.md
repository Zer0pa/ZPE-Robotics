# Gate M1-M4 Runbook: Maximalization Program

## Objective
Execute Appendix D maximalization gates with Popper-first falsification and no proxy-only closure.

## Gates
1. M1: rosbag roundtrip + live callback path checks
2. M2: LeRobot/LIBERO direct-attempt benchmark outputs
3. M3: MuJoCo replay fidelity parity attempts
4. M4: VLA token quality validation on real-task corpora attempts

## Commands
1. `RUN_ROOT="proofs/reruns/robotics_wave1_$(date -u +%Y%m%dT%H%M%SZ)"`
2. `python scripts/run_wave1.py --output-root "$RUN_ROOT" --seed 20260220 --determinism-runs 5 --max-wave`
3. `python scripts/validate_net_new.py --artifacts "$RUN_ROOT"`
4. `python scripts/net_new_ingest.py --output-root "$RUN_ROOT" --seed 20260220 --sample-size 128`
5. `/opt/homebrew/bin/python3.11 -m venv .venv_mujoco_arm64 && ./.venv_mujoco_arm64/bin/python -m pip install mujoco==3.5.0 --only-binary=:all:`
6. `PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /opt/homebrew/bin/colima start --cpu 4 --memory 8 --disk 60`

## Expected Outputs
- `max_resource_validation_log.md`
- `cross_embodiment_consistency_report.json`
- `policy_impact_delta_report.json`
- `impracticality_decisions.json`

## Fail Signatures
- Any M-gate marked `FAIL`
- Resource attempts missing command evidence
- Proxy-only closure without IMP record
- ROS2 runtime path unavailable (`ros2` missing and no viable substitute)
- Docker daemon unreachable due x86 toolchain path (`limactl is running under rosetta`, `Cannot connect to the Docker daemon`)
- MuJoCo import/runtime parity check failure under arm64 Python

## Final Status Rules
1. M1 unresolved runtime path must be emitted as explicit `FAIL` with evidence path.
2. M3 unresolved parity path must be emitted as explicit `FAIL` with evidence path.
3. Use `PAUSED_EXTERNAL` only for commercialization/license dead-ends with no commercial-safe open alternative.

## Rollback
- Patch ingestion/integration adapter minimally.
- Rerun from first failed M-gate onward.
