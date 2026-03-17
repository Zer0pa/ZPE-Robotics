from __future__ import annotations

import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import pytest
from mcap.reader import make_reader

from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture
from zpe_robotics.release_candidate import REFERENCE_ROUNDTRIP_SHA256
from zpe_robotics.rosbag_adapter import (
    ZPBAG_NATIVE_VERSION,
    decode_records,
    encode_records,
    evaluate_roundtrip,
)


def test_mcap_native_bridge_roundtrip_matches_frozen_bridge_hash(tmp_path: Path) -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260317)
    records = make_rosbag_fixture(trajectory, seed=20260318)
    codec = ZPBotCodec(keep_coeffs=8)

    blob = encode_records(records, codec, version=ZPBAG_NATIVE_VERSION)
    path = tmp_path / "arm_fixture.mcap"
    path.write_bytes(blob)

    result = evaluate_roundtrip(records, codec, version=ZPBAG_NATIVE_VERSION)
    replay_records = decode_records(path.read_bytes(), codec, decode_trajectory=False, strict_index=True)

    assert result.bit_consistent
    assert result.bytes_equal
    assert result.canonical_bridge_sha256 == REFERENCE_ROUNDTRIP_SHA256
    assert len(replay_records) == len(records)


def test_mcap_native_bridge_cli_info_reports_schema_when_available(tmp_path: Path) -> None:
    mcap_cli = shutil.which("mcap")
    if mcap_cli is None:
        pytest.skip("mcap CLI not installed")

    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260317)
    records = make_rosbag_fixture(trajectory, seed=20260318)
    codec = ZPBotCodec(keep_coeffs=8)
    path = tmp_path / "arm_fixture.mcap"
    path.write_bytes(encode_records(records, codec, version=ZPBAG_NATIVE_VERSION))

    completed = subprocess.run([mcap_cli, "info", str(path)], check=True, capture_output=True, text=True)
    stdout = completed.stdout.strip()
    assert stdout
    assert "zpbag2" in stdout
    assert "/joint_states" in stdout

    schema, channel, _ = next(make_reader(BytesIO(path.read_bytes()), validate_crcs=True).iter_messages())
    assert schema is not None
    assert schema.encoding == "zpbag2"
    assert channel.message_encoding == "compass8"
