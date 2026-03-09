# Claim Status Delta

| Claim | Status | Metric | Threshold | Evidence |
|---|---|---:|---|---|
| ROB-C001 | PASS | 238.024213 | >= 15 | robot_arm_benchmark.json |
| ROB-C002 | PASS | 215.578947 | >= 12 | robot_humanoid_benchmark.json |
| ROB-C003 | PASS | 0.000008 | <= 0.1 mm | robot_ee_fidelity.json |
| ROB-C004 | PASS | 0.000001 | <= 0.05 deg | robot_joint_fidelity.json |
| ROB-C005 | PASS | 1.000000 | >= 0.90 | robot_primitive_search_eval.json |
| ROB-C006 | PASS | 1.000000 | == 1.0 | robot_rosbag_roundtrip.json |
| ROB-C007 | PASS | 1.000000 | >= 0.90 | robot_anomaly_eval.json |
| ROB-C008 | PASS | 0.474359 | >= 0.0 | robot_vla_token_eval.json |

| Max Claim | Status | Metric | Threshold | Evidence |
|---|---|---|---|---|
| MAX-M1 | PASS | RESOLVED | RESOLVED | ros2_runtime_probe.json |
| MAX-M2 | PASS | RESOLVED | RESOLVED | max_resource_validation_log.md |
| MAX-M3 | PASS | RESOLVED | RESOLVED | mujoco_parity_report.json |
| MAX-E3-OCTO | PASS | RESOLVED | RESOLVED | policy_impact_delta_report.json |
