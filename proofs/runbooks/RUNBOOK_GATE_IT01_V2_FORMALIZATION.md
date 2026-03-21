# Gate IT-01 Runbook: ZPBOT V2 Formalization

## Objective

Revalidate the Phase-2 packet authority surface after any change to the codec, wire parser, or protocol docs.

## Commands

1. `python -m pytest tests/test_codec.py tests/test_wire.py -q`
2. `python - <<'PY'`
   `from pathlib import Path`
   `from zpe_robotics.codec import ZPBotCodec`
   `from zpe_robotics.fixtures import generate_joint_trajectory`
   `from zpe_robotics.utils import write_json`
   `from zpe_robotics.wire import describe_packet`
   `trajectory = generate_joint_trajectory(num_frames=2048, num_joints=6, seed=20260317)`
   `blob = ZPBotCodec(keep_coeffs=8).encode(trajectory)`
   `write_json(Path("proofs/reruns/it01_wire_probe_current/it01_wire_probe.json"), describe_packet(blob))`
   `PY`

## Expected Outputs

- `proofs/reruns/it01_wire_probe_current/it01_wire_probe.json`
- passing `tests/test_codec.py`
- passing `tests/test_wire.py`

## Pass Condition

- The packet description reports `authority_surface = zpbot-v2`, `compatibility_mode = wire-v1`, and `wire_version = 1`.
- The parser accepts valid packets and rejects bad magic, CRC, truncation, and unsupported versions.

## Fail Signatures

- `unsupported codec version`
- `payload CRC mismatch`
- packet tests fail
- any edit widens the packet surface into v3 semantics

## Scope Guard

This runbook validates the externalized packet surface only. It does not close `IT-02`, `M1`, or any later integration gate.
