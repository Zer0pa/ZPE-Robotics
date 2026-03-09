# Commercialization Risk Register

| Risk ID | Risk | Status | Action | Evidence |
|---|---|---|---|---|
| CMR-001 | AgiBot World primary dataset is gated and may constrain commercial portability | MITIGATED | Use open fallback dataset (`weijian-sun/agibotworld-lerobot`) with deterministic subset policy | impracticality_decisions.json; max_resource_validation_log.md |
| CMR-002 | OpenX primary loader is script-based and unsupported in current datasets runtime | MITIGATED | Use open fallback dataset (`IVC-liuyuan/Swift-OpenX-Embodiment-action-chunk-jsons`) | impracticality_decisions.json; cross_embodiment_consistency_report.json |
| CMR-003 | Runtime closure depends on local virtualization stack compatibility | MITIGATED | Enforce arm64 Colima startup path and Docker runtime verification before M1 adjudication | ros2_runtime_probe.json; max_resource_validation_log.md |
| CMR-004 | Octo comparator dependency drift may break repeatability | MITIGATED | Pin Octo runtime and validate comparator execution in arm64 environment before gate promotion | policy_impact_delta_report.json; max_resource_validation_log.md |

## Verdict
- commercialization_status: SAFE
- paused_external_claims: 0
- note: No claim is currently blocked solely by non-commercial licensing constraints.
