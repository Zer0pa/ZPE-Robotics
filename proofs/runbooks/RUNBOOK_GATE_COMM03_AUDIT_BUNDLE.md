# RUNBOOK_GATE_COMM03_AUDIT_BUNDLE

## Purpose

Verify the bounded COMM-03 Mac audit-bundle evidence without widening into
device-native replay, ROS2 parity, or safety certification.

## Inputs

- `proofs/comm03/comm03_provenance_manifest.json`
- `proofs/comm03/comm03_corruption_matrix.json`
- `proofs/comm03/comm03_mac_audit_result.json`
- `proofs/comm03/COMM03_AUDIT_REPLAY_BUNDLE.md`

## Acceptance Gate

- The provenance manifest records the canonical packet SHA-256.
- The corruption matrix is present and committed.
- The Mac audit result is present and committed.
- `proofs/comm03/COMM03_AUDIT_REPLAY_BUNDLE.md` remains a bounded audit claim only.

## Failure Mode

If any input is missing, COMM-03 remains historical/supporting context and must
not be promoted as current release readiness.
