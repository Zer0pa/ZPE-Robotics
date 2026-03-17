"""Popper-first falsification campaigns for Wave-1 claims."""

from __future__ import annotations

from .anomaly import detect_anomalies
from .codec import ZPBotCodec, compression_ratio
from .fixtures import FixtureBundle, malformed_trajectory_inputs
from .kinematics import ee_rmse_mm, rmse_deg
from .primitives import PrimitiveSample, confusion_stress
from .rosbag_adapter import BagFormatError, corrupt_blob, decode_records, encode_records, reorder_records
from .utils import sha256_bytes, stable_json_dumps


def run_falsification_campaigns(
    codec_arm: ZPBotCodec,
    codec_humanoid: ZPBotCodec,
    fixtures: FixtureBundle,
    rosbag_records: list[dict],
    primitive_library: list[PrimitiveSample],
    seed: int,
) -> dict:
    dt1 = _campaign_malformed(codec_arm)
    dt2 = _campaign_adversarial(codec_arm, codec_humanoid, fixtures)
    dt3 = _campaign_rosbag(codec_arm, rosbag_records)
    dt4 = _campaign_determinism(codec_arm, fixtures)
    dt5 = _campaign_primitive_confusion(primitive_library, seed)

    uncaught_crashes = 0
    for campaign in (dt1, dt2, dt3, dt4, dt5):
        uncaught_crashes += int(campaign.get("uncaught_crashes", 0))

    return {
        "DT-ROB-1": dt1,
        "DT-ROB-2": dt2,
        "DT-ROB-3": dt3,
        "DT-ROB-4": dt4,
        "DT-ROB-5": dt5,
        "uncaught_crashes": uncaught_crashes,
        "pass": bool(uncaught_crashes == 0 and all(c["pass"] for c in (dt1, dt2, dt3, dt4, dt5))),
    }


def _campaign_malformed(codec: ZPBotCodec) -> dict:
    handled = 0
    failures = []

    for idx, malformed in enumerate(malformed_trajectory_inputs()):
        try:
            codec.encode(malformed)
            failures.append(f"malformed_case_{idx}: accepted_invalid_input")
        except Exception:
            handled += 1

    total = len(malformed_trajectory_inputs())
    return {
        "handled": handled,
        "total": total,
        "uncaught_crashes": 0,
        "pass": bool(handled == total),
        "failures": failures,
    }


def _campaign_adversarial(codec_arm: ZPBotCodec, codec_humanoid: ZPBotCodec, fixtures: FixtureBundle) -> dict:
    try:
        arm_blob = codec_arm.encode(fixtures.arm_adversarial)
        arm_recon = codec_arm.decode(arm_blob)
        hum_blob = codec_humanoid.encode(fixtures.humanoid_adversarial)
        hum_recon = codec_humanoid.decode(hum_blob)

        arm_joint_rmse = rmse_deg(fixtures.arm_adversarial, arm_recon)
        arm_ee_rmse = ee_rmse_mm(fixtures.arm_adversarial, arm_recon)
        hum_joint_rmse = rmse_deg(fixtures.humanoid_adversarial, hum_recon)

        arm_cr = compression_ratio(fixtures.arm_adversarial, arm_blob)
        hum_cr = compression_ratio(fixtures.humanoid_adversarial, hum_blob)

        anomalies = detect_anomalies(fixtures.arm_adversarial)
        anomaly_rate = float(anomalies.mean())

        return {
            "arm_joint_rmse_deg": float(arm_joint_rmse),
            "arm_ee_rmse_mm": float(arm_ee_rmse),
            "humanoid_joint_rmse_deg": float(hum_joint_rmse),
            "arm_compression_ratio": float(arm_cr),
            "humanoid_compression_ratio": float(hum_cr),
            "anomaly_flag_rate": float(anomaly_rate),
            "uncaught_crashes": 0,
            "pass": bool(arm_cr > 1.0 and hum_cr > 1.0),
        }
    except Exception as exc:
        return {
            "uncaught_crashes": 1,
            "pass": False,
            "error": str(exc),
        }


def _campaign_rosbag(codec: ZPBotCodec, records: list[dict]) -> dict:
    try:
        blob = encode_records(records, codec)

        corruption_detected = False
        try:
            decode_records(corrupt_blob(blob), codec, strict_index=True)
        except BagFormatError:
            corruption_detected = True

        reorder_detected = False
        reordered_blob = encode_records(reorder_records(records), codec)
        try:
            decode_records(reordered_blob, codec, strict_index=True)
        except BagFormatError:
            reorder_detected = True

        return {
            "corruption_detected": bool(corruption_detected),
            "reorder_detected": bool(reorder_detected),
            "uncaught_crashes": 0,
            "pass": bool(corruption_detected and reorder_detected),
        }
    except Exception as exc:
        return {
            "uncaught_crashes": 1,
            "pass": False,
            "error": str(exc),
        }


def _campaign_determinism(codec: ZPBotCodec, fixtures: FixtureBundle) -> dict:
    try:
        hashes = []
        for _ in range(5):
            blob = codec.encode(fixtures.arm_nominal)
            hashes.append(sha256_bytes(blob))

        return {
            "hashes": hashes,
            "unique_hashes": len(set(hashes)),
            "uncaught_crashes": 0,
            "pass": bool(len(set(hashes)) == 1),
        }
    except Exception as exc:
        return {
            "uncaught_crashes": 1,
            "pass": False,
            "error": str(exc),
        }


def _campaign_primitive_confusion(library: list[PrimitiveSample], seed: int) -> dict:
    try:
        stress = confusion_stress(library, seed=seed + 77, count=120, k=10)
        return {
            **stress,
            "uncaught_crashes": 0,
        }
    except Exception as exc:
        return {
            "uncaught_crashes": 1,
            "pass": False,
            "error": str(exc),
        }


def render_falsification_markdown(results: dict) -> str:
    lines = [
        "# Falsification Results",
        "",
        "Popper-first campaigns executed before claim promotion.",
        "",
    ]

    for campaign_id in ("DT-ROB-1", "DT-ROB-2", "DT-ROB-3", "DT-ROB-4", "DT-ROB-5"):
        payload = results[campaign_id]
        lines.append(f"## {campaign_id}")
        lines.append(f"- pass: {payload.get('pass')}")
        lines.append(f"- uncaught_crashes: {payload.get('uncaught_crashes', 0)}")
        for key, value in payload.items():
            if key in {"pass", "uncaught_crashes"}:
                continue
            lines.append(f"- {key}: {value}")
        lines.append("")

    lines.append(f"Total uncaught crashes: {results.get('uncaught_crashes', 0)}")
    lines.append(f"Overall pass: {results.get('pass')}")
    return "\n".join(lines) + "\n"


def falsification_hash(results: dict) -> str:
    return sha256_bytes(stable_json_dumps(results).encode("utf-8"))
