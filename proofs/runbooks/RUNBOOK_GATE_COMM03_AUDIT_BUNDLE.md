# Gate COMM-03 Runbook: Audit Bundle

## Objective

Generate the compact COMM-03 audit bundle for the canonical published packet without changing the frozen `zpbot-v2` or `wire-v1` contract.

## Preconditions

- Repo root is `/Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`
- `proofs/release_candidate/canonical_release_packet.zpbot` exists
- The working environment can run the local test subset and the `zpe` CLI

## Commands

1. `pip install -e .`
2. `pytest tests/test_wire.py tests/test_audit_bundle.py tests/test_cli.py`
3. `zpe audit-bundle proofs/release_candidate/canonical_release_packet.zpbot proofs/comm03`

## Expected Output

- `proofs/comm03/comm03_provenance_manifest.json`
- `proofs/comm03/comm03_corruption_matrix.json`

## Pass Condition

The COMM-03 audit bundle is `PASS` only when:

- the manifest records `authority_surface = zpbot-v2` and `compatibility_mode = wire-v1`,
- the packet SHA-256 is present,
- the replay SHA-256 is present and tied to the frozen bridge anchor,
- the corruption matrix records explicit failures for invalid magic, CRC mismatch, truncated header, and unsupported version.

## Explicit Non-Claims

- This runbook does not claim safety certification.
- This runbook does not claim RedMagic device execution.
- This runbook does not authorize RunPod use.
