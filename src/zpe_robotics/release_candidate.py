"""Helpers for Phase 4 release-candidate and parity artifacts."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .codec import ZPBotCodec
from .constants import DEFAULT_SEED, DEFAULT_TRAJECTORY_TOPIC
from .fixtures import build_fixture_bundle, generate_joint_trajectory, make_rosbag_fixture
from .mcap_bridge import evaluate_bridge_roundtrip
from .rosbag_adapter import decode_records, encode_records
from .utils import sha256_bytes


REFERENCE_ROUNDTRIP_SHA256 = "a0941be23dc19bf96d7ec2e25f7ede9c051c3b28f51f141b89fdfc2691c3e125"
REFERENCE_TRAJECTORY_SEED = 20260317
REFERENCE_RECORD_SEED = 20260318
DEFAULT_ROBOT_NAME = "zpe_motion_kernel"


@dataclass(frozen=True)
class CompositionArtifacts:
    trajectory: np.ndarray
    packet: bytes
    bag_blob: bytes


def default_codec() -> ZPBotCodec:
    return ZPBotCodec(keep_coeffs=8)


def build_canonical_arm_fixture(seed: int = DEFAULT_SEED) -> np.ndarray:
    return build_fixture_bundle(seed).arm_nominal


def build_canonical_record(seed: int = DEFAULT_SEED) -> dict[str, object]:
    return build_default_bag_record(build_canonical_arm_fixture(seed))


def build_single_packet_composition(codec: ZPBotCodec | None = None, seed: int = DEFAULT_SEED) -> CompositionArtifacts:
    active_codec = codec or default_codec()
    record = build_canonical_record(seed)
    trajectory = np.asarray(record["trajectory"], dtype=np.float64)
    packet = active_codec.encode(trajectory)
    bag_blob = encode_records([record], active_codec)
    return CompositionArtifacts(trajectory=trajectory, packet=packet, bag_blob=bag_blob)


def decode_single_packet_bag(bag_blob: bytes, codec: ZPBotCodec | None = None) -> np.ndarray:
    active_codec = codec or default_codec()
    records = decode_records(bag_blob, active_codec, decode_trajectory=True, strict_index=True)
    if len(records) != 1:
        raise ValueError("expected exactly one record in deterministic bag envelope")
    return np.asarray(records[0]["trajectory"], dtype=np.float64)


def build_default_bag_record(trajectory: np.ndarray) -> dict[str, object]:
    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("trajectory must be 2D")
    joint_names = [f"joint_{idx}" for idx in range(arr.shape[1])]
    return {
        "index": 0,
        "topic": DEFAULT_TRAJECTORY_TOPIC,
        "timestamp_ns": 1_700_000_000_000_000_000,
        "robot": DEFAULT_ROBOT_NAME,
        "joint_names": joint_names,
        "trajectory": arr,
        "quality": 1.0,
    }


def encode_single_record_bag(trajectory: np.ndarray, codec: ZPBotCodec | None = None) -> bytes:
    active_codec = codec or default_codec()
    return encode_records([build_default_bag_record(trajectory)], active_codec)


def compute_reference_bridge_roundtrip(codec: ZPBotCodec | None = None) -> dict[str, object]:
    active_codec = codec or default_codec()
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=REFERENCE_TRAJECTORY_SEED)
    records = make_rosbag_fixture(trajectory, seed=REFERENCE_RECORD_SEED)
    result = evaluate_bridge_roundtrip(records, active_codec)
    return {
        "bit_consistent": bool(result.bit_consistent),
        "bytes_equal": bool(result.bytes_equal),
        "original_sha256": result.original_sha256,
        "replay_sha256": result.replay_sha256,
        "records": int(result.records),
    }


def raw_float32_bytes(trajectory: np.ndarray) -> bytes:
    arr = np.asarray(trajectory, dtype=np.float32)
    return arr.tobytes(order="C")


def raw_float32_sha256(trajectory: np.ndarray) -> str:
    return sha256_bytes(raw_float32_bytes(trajectory))
