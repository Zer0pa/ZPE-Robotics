<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Claim Boundary

This file is the active claim boundary for the narrowed Robotics execution
gate.

## Selected Gate

| Field | Current truth |
|---|---|
| Gate | bounded-lossy archive/search |
| Gate status | pass for the narrow claim only |
| Full engineering status | not complete |
| Gate proof | `../proofs/narrow_claim/NARROW_CLAIM_GATE.json` |
| Governing blocker proof | `../proofs/ENGINEERING_BLOCKERS.md` |

## Ratified Surface

ZPE-Robotics is an archive/replay evidence surface for ordered robot joint
streams. The ratified surface is:

- bounded-lossy `.zpbot` archive/replay infrastructure
- decoded PrimitiveIndex search
- packet integrity and auditability on the `zpbot-v2` / `wire-v1` surface
- VLA token export
- benchmark spread reporting across qualified LeRobot datasets
- threshold-selected attack-5 anomaly evidence on the declared Phase 10 holdout
  surface

## Non-Claims

The active surface does not claim:

- lossless replay
- bit-exact replay
- search without decode
- live robot control
- Robotics Rust ABI routing through ZPE-IMC
- general anomaly readiness outside the declared holdout surface
- independent third-party reproduction
- full release readiness

## Authority

If this file conflicts with a proof artifact, the proof artifact wins. Use the
reading order in `../proofs/README_LINEAGE_PATHS.md`.
