# Residual Risk Register

| Risk ID | Risk | Status | Mitigation | Evidence |
|---|---|---|---|---|
| R-001 | External dataset comparability to LIBERO-100 | CLOSED | Keep direct LIBERO benchmark in regression | max_resource_validation_log.md |
| R-002 | Native ROS2/MoveIt2 runtime interoperability | CLOSED | Execute ROS2 runtime path where unavailable | max_resource_validation_log.md |
| R-003 | MuJoCo physics parity | CLOSED | Execute MuJoCo runtime parity path | max_resource_validation_log.md |
| R-004 | Octo policy comparator runtime | CLOSED | Execute comparator on RunPod when IMP-COMPUTE present | policy_impact_delta_report.json |
| R-005 | Falsification uncaught crash count = 0 | CLOSED | Keep campaign in regression pack | falsification_results.md |
| R-006 | Determinism unique hash count = 1 | CLOSED | Keep 5/5 replay gate hard-fail | determinism_replay_results.json |
