"""Constants for ZPE Robotics Wave-1 execution."""

from __future__ import annotations

DEFAULT_SEED = 20260220
WAVE1_ARTIFACT_TAG = "2026-02-20_zpe_robotics_wave1"

CLAIM_THRESHOLDS = {
    "ROB-C001": 15.0,
    "ROB-C002": 12.0,
    "ROB-C003": 0.1,
    "ROB-C004": 0.05,
    "ROB-C005": 0.90,
    "ROB-C006": 1.0,
    "ROB-C007": 0.90,
    "ROB-C008": 0.0,
}

PRD_CORE_ARTIFACTS = [
    "handoff_manifest.json",
    "before_after_metrics.json",
    "falsification_results.md",
    "claim_status_delta.md",
    "command_log.txt",
    "robot_arm_benchmark.json",
    "robot_humanoid_benchmark.json",
    "robot_ee_fidelity.json",
    "robot_joint_fidelity.json",
    "robot_primitive_search_eval.json",
    "robot_rosbag_roundtrip.json",
    "robot_anomaly_eval.json",
    "robot_vla_token_eval.json",
    "determinism_replay_results.json",
    "regression_results.txt",
]

APPENDIX_C_ARTIFACTS = [
    "quality_gate_scorecard.json",
    "innovation_delta_report.md",
    "integration_readiness_contract.json",
    "residual_risk_register.md",
    "concept_open_questions_resolution.md",
    "concept_resource_traceability.json",
]

APPENDIX_E_ARTIFACTS = [
    "max_resource_lock.json",
    "max_resource_validation_log.md",
    "max_claim_resource_map.json",
    "impracticality_decisions.json",
    "cross_embodiment_consistency_report.json",
    "policy_impact_delta_report.json",
    "net_new_gap_closure_matrix.json",
]

RUNPOD_DEFERMENT_ARTIFACTS = [
    "runpod_readiness_manifest.json",
    "runpod_exec_plan.md",
    "runpod_requirements_lock.txt",
    "runpod_expected_artifacts_manifest.json",
]

ALLOWED_IMP_CODES = {"IMP-LICENSE", "IMP-ACCESS", "IMP-COMPUTE", "IMP-STORAGE", "IMP-NOCODE"}

REQUIRED_ARTIFACTS = PRD_CORE_ARTIFACTS + APPENDIX_C_ARTIFACTS

AUTHORITY_SURFACE = "zpbot-v2"
AUTHORITY_WIRE_COMPATIBILITY = "wire-v1"

MAGIC_ZPBOT = b"ZPBOT"
CODEC_VERSION = 1
ZPBOT_HEADER_FORMAT = "<5sB I H H I"

ZPBOT_MESSAGE_ENCODING = "zpbot"

ZPBAG_MAGIC = b"ZPBAG1"
ZPBAG_HEADER_FORMAT = "<6sII"
ZPBAG_SCHEMA_NAME = "zpe_rosbag_wave1"
ZPBAG_SCHEMA_VERSION = 1
ZPBAG_LEGACY_VERSION = "zpbag1"
ZPBAG_NATIVE_VERSION = "zpbag2"
ZPBAG_NATIVE_PROFILE = "zpe_mcap_bridge_v2"
ZPBAG_NATIVE_SCHEMA_ENCODING = "zpbag2"
ZPBAG_NATIVE_MESSAGE_ENCODING = "compass8"
ZPBAG_NATIVE_INDEX_NAME = "zpe.record_index"
MCAP_MAGIC = b"\x89MCAP0\r\n"

MCAP_BRIDGE_MAGIC = b"ZPMCAP1"
MCAP_BRIDGE_HEADER_FORMAT = "<7sII"
MCAP_BRIDGE_PROFILE = "zpe_mcap_bridge_v1"
MCAP_BRIDGE_SCHEMA_NAME = "zpe.robotics.zpbot_packet"
MCAP_BRIDGE_SCHEMA_ENCODING = "application/json"
MCAP_BRIDGE_MESSAGE_ENCODING = ZPBOT_MESSAGE_ENCODING

DEFAULT_TRAJECTORY_TOPIC = "/joint_states"
ROS2_BRIDGE_PASS_CRITERIA = (
    "ros2 executable and MoveIt2 package discovery through local or container runtime path, "
    "plus an importable MCAP bridge entrypoint"
)
