# Gate ARM64 Runbook: GitHub Actions Parity Probe

## Objective

Pressure deterministic bridge stability through a hosted ARM64 parity precheck anchored to the frozen Phase-2 bridge hash.

## Frozen Reference

- `x86_reference_sha256 = a0941be23dc19bf96d7ec2e25f7ede9c051c3b28f51f141b89fdfc2691c3e125`
- source artifact: `proofs/reruns/robotics_phase2_local_2026-03-17/mcap_bridge_roundtrip.json`
- fixture path:
  - `generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260317)`
  - `make_rosbag_fixture(..., seed=20260318)`
  - `ZPBotCodec(keep_coeffs=8)`

## Local Recompute

```bash
PYTHONPATH=src python - <<'PY'
from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture
from zpe_robotics.mcap_bridge import evaluate_bridge_roundtrip
trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260317)
records = make_rosbag_fixture(trajectory, seed=20260318)
result = evaluate_bridge_roundtrip(records, ZPBotCodec(keep_coeffs=8))
print(result.original_sha256)
PY
```

## Hosted Run

1. Push the workflow-bearing branch to GitHub.
2. Dispatch `.github/workflows/arm64_parity_probe.yml`.
3. Download artifact `arm64-parity-evidence`.

## Expected Output

- `proofs/reruns/arm64_parity_probe_<run-id>/arm64_parity_result.json`

## Pass Condition

The hosted artifact reports:

- `status = PASS`
- `hashes_match = true`
- `roundtrip_sha256` equal to the frozen reference hash
- required provenance fields:
  - `authority_surface = zpbot-v2`
  - `compatibility_mode = wire-v1`
  - `generation_timestamp`
  - `host_platform`
  - `workflow_run_id`

## Fail Signatures

- local recompute drift from the frozen reference
- artifact missing
- `hashes_match = false`
- missing provenance fields

## Scope Guard

- This runbook stages a hosted ARM64 parity precheck.
- It does not prove native Jetson parity or full ARM deployment closure on its own.
