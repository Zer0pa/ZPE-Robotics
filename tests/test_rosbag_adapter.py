from __future__ import annotations

import pytest

from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture
from zpe_robotics.rosbag_adapter import BagFormatError, corrupt_blob, decode_records, encode_records, evaluate_roundtrip


def test_rosbag_roundtrip_is_bit_consistent() -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=77)
    records = make_rosbag_fixture(trajectory, seed=91)
    codec = ZPBotCodec(keep_coeffs=8)

    result = evaluate_roundtrip(records, codec)
    assert result.bit_consistent
    assert result.bytes_equal


def test_corruption_detection() -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=88)
    records = make_rosbag_fixture(trajectory, seed=92)
    codec = ZPBotCodec(keep_coeffs=8)

    blob = encode_records(records, codec)
    bad = corrupt_blob(blob)

    with pytest.raises(BagFormatError):
        decode_records(bad, codec, strict_index=True)

