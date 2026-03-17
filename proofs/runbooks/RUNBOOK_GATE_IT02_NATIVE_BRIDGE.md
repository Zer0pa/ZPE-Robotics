# Gate IT-02 Runbook: Native Bridge Probe

## Objective

Exercise the first MCAP-aligned bridge surface and produce explicit runtime evidence for the minimum ROS2 plus MoveIt2 path.

## Commands

1. `python -m pytest tests/test_rosbag_adapter.py tests/test_mcap_bridge.py -q`
2. `python - <<'PY'`
   `from pathlib import Path`
   `from zpe_robotics.codec import ZPBotCodec`
   `from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture`
   `from zpe_robotics.mcap_bridge import evaluate_bridge_roundtrip`
   `from zpe_robotics.utils import write_json`
   `trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260317)`
   `records = make_rosbag_fixture(trajectory, seed=20260318)`
   `result = evaluate_bridge_roundtrip(records, ZPBotCodec(keep_coeffs=8))`
   `write_json(Path("proofs/reruns/robotics_phase2_local_2026-03-17/mcap_bridge_roundtrip.json"), result.__dict__)`
   `PY`
3. `python scripts/ros2_bridge_probe.py --output proofs/reruns/robotics_phase2_local_2026-03-17/ros2_bridge_probe.json`

## Expected Outputs

- `proofs/reruns/robotics_phase2_local_2026-03-17/mcap_bridge_roundtrip.json`
- `proofs/reruns/robotics_phase2_local_2026-03-17/ros2_bridge_probe.json`
- passing `tests/test_rosbag_adapter.py`
- passing `tests/test_mcap_bridge.py`

## Pass Condition

- The MCAP-aligned bridge roundtrip remains bit-consistent.
- The probe artifact exists and records a real `runtime_path`, attempt log, and bridge import status.
- If the runtime path is unavailable, the artifact must still preserve explicit blocker evidence instead of converting the result into a pass.

## Fail Signatures

- `bridge CRC mismatch`
- `bridge message sequence violation`
- the bridge module is not importable
- `ros2_bridge_probe.json` missing, empty, or missing command attempts

## Scope Guard

This runbook makes `IT-02` runnable. It does not claim that `M1` is closed unless the probe artifact itself reports `status = PASS`.
