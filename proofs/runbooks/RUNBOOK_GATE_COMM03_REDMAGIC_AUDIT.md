# RUNBOOK_GATE_COMM03_REDMAGIC_AUDIT

## Purpose

Verify the bounded RedMagic packet-hash visibility evidence for COMM-03.

## Inputs

- `proofs/comm03/comm03_redmagic_device_result.json`
- `proofs/comm03/comm03_redmagic_termux_audit.png`
- `proofs/comm03/comm03_provenance_manifest.json`
- `proofs/comm03/COMM03_AUDIT_REPLAY_BUNDLE.md`

## Acceptance Gate

- Device-side packet SHA-256 matches the Mac-side packet hash recorded in the
  provenance manifest.
- Screenshot evidence remains committed.
- The claim stays limited to foreground Termux packet-hash visibility.

## Failure Mode

If hash visibility cannot be verified from committed artifacts, do not claim
device-side audit visibility for COMM-03.
