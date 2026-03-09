# Residual Risk Register

| Risk ID | Risk | Status | Mitigation | Evidence |
|---|---|---|---|---|
| R-001 | External dataset comparability to LIBERO-100 | CLOSED | Keep direct LIBERO benchmark in regression | max_resource_validation_log.md |
| R-002 | Native ROS2/MoveIt2 runtime interoperability | CLOSED | Enforce arm64 Colima recovery and revalidate live ROS2 + MoveIt package path | ros2_runtime_probe.json; max_resource_validation_log.md |
| R-003 | MuJoCo physics parity | CLOSED | Execute MuJoCo runtime parity path | max_resource_validation_log.md |
| R-004 | Octo policy comparator runtime | CLOSED | Repair local Octo dependency chain and rerun comparator on arm64 runtime | policy_impact_delta_report.json; max_resource_validation_log.md |
| R-005 | Falsification uncaught crash count = 0 | CLOSED | Keep campaign in regression pack | falsification_results.md |
| R-006 | Determinism unique hash count = 1 | CLOSED | Keep 5/5 replay gate hard-fail | determinism_replay_results.json |
