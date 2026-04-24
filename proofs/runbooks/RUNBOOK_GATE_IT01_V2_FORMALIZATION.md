# RUNBOOK_GATE_IT01_V2_FORMALIZATION

## Purpose

Verify that the public `zpbot-v2` authority surface remains compatible with the
current `wire-v1` packet implementation.

## Inputs

- `docs/ZPBOT_V2_AUTHORITY_SURFACE.md`
- `src/zpe_robotics/wire.py`
- `tests/test_wire.py`
- `proofs/release_candidate/canonical_release_packet.zpbot`

## Commands

```bash
python -m pytest tests/test_wire.py tests/test_release_candidate.py -q
zpe-robotics verify proofs/release_candidate/canonical_release_packet.zpbot
zpe-robotics info proofs/release_candidate/canonical_release_packet.zpbot
```

## Acceptance Gate

- Packet tests pass.
- CLI verification accepts the canonical packet.
- The authority surface remains `zpbot-v2` over `wire-v1`.

## Failure Mode

If packet tests or CLI verification fail, do not update README claims. Keep the
failure in blocker-facing artifacts until the packet path is repaired and rerun.
