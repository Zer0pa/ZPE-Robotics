# Narrow Claim Ratification

Date: 2026-04-24

## Gate Decision

The selected execution gate is the narrow-claim gate.

The technical-closure gate is rejected for this PRD execution because the
available evidence still fails benchmark gate `B3`, red-team attack `3`, and
the Robotics Rust ABI route. Claiming those as closed would reward the wrong
objective.

## Ratified Claim

ZPE-Robotics is ratified only as a bounded-lossy robot motion telemetry archive
and replay-evidence surface.

The active claim includes:

- bounded-lossy `.zpbot` archive/replay infrastructure for ordered joint-stream
  logs
- decoded PrimitiveIndex search
- packet integrity and auditability on the `zpbot-v2` / `wire-v1` surface
- VLA token export as secondary integration evidence
- multi-dataset LeRobot benchmark breadth with preserved spread and failures
- threshold-selected attack-5 anomaly evidence on the declared Phase 10 holdout
  surface

## Explicit Non-Claims

The active product surface does not claim:

- lossless or bit-exact replay
- search without decode
- live robot control
- Robotics Rust ABI routing through ZPE-IMC
- general anomaly readiness outside the declared holdout surface
- external third-party reproduction
- full release readiness

## Evidence

| Question | Current answer | Authority |
|---|---|---|
| Is the narrow archive/search claim ratified? | yes | `proofs/narrow_claim/NARROW_CLAIM_GATE.json` |
| Is full engineering complete? | no | `proofs/ENGINEERING_BLOCKERS.md` |
| Did `B3` close? | no | `proofs/enterprise_benchmark/GATE_VERDICTS.json` |
| Did attack `3` close? | no | `proofs/red_team/red_team_report.json` |
| Did attack `5` close on the declared surface? | yes | `proofs/release_candidate/anomaly_detection_result.json` |
| Is Robotics routed through a Rust ABI? | no | `proofs/imc_audit/imc_architecture_audit.json` |
| Is external reproduction closed? | no | `proofs/red_team/red_team_report.json` |

## Result

The PRD execution is complete for the narrowed bounded-lossy archive/search
claim. It is not a full technical-closure certificate and must not be reused as
one.
