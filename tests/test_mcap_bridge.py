from __future__ import annotations

import pytest

from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture
from zpe_robotics.mcap_bridge import (
    BridgeFormatError,
    corrupt_blob,
    decode_bridge_records,
    encode_bridge_records,
    evaluate_bridge_roundtrip,
    resequence_blob,
)


def test_mcap_bridge_roundtrip_is_bit_consistent() -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=515)
    records = make_rosbag_fixture(trajectory, seed=616)
    codec = ZPBotCodec(keep_coeffs=8)

    result = evaluate_bridge_roundtrip(records, codec)
    assert result.bit_consistent
    assert result.bytes_equal


def test_mcap_bridge_corruption_detection() -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=717)
    records = make_rosbag_fixture(trajectory, seed=818)
    codec = ZPBotCodec(keep_coeffs=8)

    blob = encode_bridge_records(records, codec)
    with pytest.raises(BridgeFormatError, match="bridge CRC mismatch"):
        decode_bridge_records(corrupt_blob(blob), codec)


def test_mcap_bridge_sequence_violation_is_detected() -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=919)
    records = make_rosbag_fixture(trajectory, seed=1020)
    codec = ZPBotCodec(keep_coeffs=8)

    blob = encode_bridge_records(records, codec)
    with pytest.raises(BridgeFormatError, match="bridge message sequence violation"):
        decode_bridge_records(resequence_blob(blob), codec, strict_sequence=True)
