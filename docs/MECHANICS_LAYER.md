<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Mechanics Layer

This mechanics layer is scoped to the narrowed Robotics archive/search gate.
It is not a platform claim and does not add a live-control surface.

| Field | Current value |
|---|---|
| Object basis | ordered robot joint-stream logs / motion telemetry |
| Object currency | frames, joint dimensions, FPS, episodes, `.zpbot` packets, CRC32 integrity, dataset revision pins |
| Transform | bounded-lossy spectral packet/archive transform plus packet integrity and decoded PrimitiveIndex search |
| Preserved surface | compression and latency on qualified LeRobot datasets; CRC integrity; replay under bounded lossy error; VLA token export |
| Failure surface | no general bit-exact replay; no search without decode; step/discontinuous inputs can show Gibbs ringing; attack `3` failed; `B3` failed; attack `7` open |
| Authority anchors | `../proofs/ENGINEERING_BLOCKERS.md`, `../proofs/narrow_claim/NARROW_CLAIM_GATE.json`, `../proofs/enterprise_benchmark/GATE_VERDICTS.json`, `../proofs/red_team/red_team_report.json`, `../proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`, `../proofs/release_candidate/anomaly_detection_result.json` |
| State label | bounded positive for smooth/archive surfaces; full engineering remains blocked |

## Labels

- `SPECTRAL ARCHIVE`
- `NOT-CONTROL-LOOP`
- `RED-TEAM-ATTACK-7-OPEN`
