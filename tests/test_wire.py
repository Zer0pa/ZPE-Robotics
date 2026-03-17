from __future__ import annotations

import numpy as np
import pytest

from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY, CODEC_VERSION
from zpe_robotics.fixtures import generate_joint_trajectory
from zpe_robotics.wire import HEADER_SIZE, WireFormatError, decode_packet, describe_packet, parse_packet_header


def test_parse_packet_header_exposes_authority_alias() -> None:
    trajectory = generate_joint_trajectory(num_frames=2048, num_joints=6, seed=1234)
    blob = ZPBotCodec(keep_coeffs=8).encode(trajectory)

    header = parse_packet_header(blob)
    description = describe_packet(blob)

    assert header.authority_surface == AUTHORITY_SURFACE
    assert header.compatibility_mode == AUTHORITY_WIRE_COMPATIBILITY
    assert header.wire_version == CODEC_VERSION
    assert description["authority_surface"] == AUTHORITY_SURFACE
    assert description["wire_version"] == CODEC_VERSION


def test_wire_decode_matches_codec_decode() -> None:
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=4321)
    codec = ZPBotCodec(keep_coeffs=8)
    blob = codec.encode(trajectory)

    expected = codec.decode(blob)
    observed = decode_packet(blob)

    np.testing.assert_allclose(observed, expected, rtol=0.0, atol=0.0)


def test_crc_and_magic_errors_are_rejected() -> None:
    trajectory = generate_joint_trajectory(num_frames=1024, num_joints=4, seed=909)
    blob = ZPBotCodec(keep_coeffs=8).encode(trajectory)

    bad_magic = b"BAD!!" + blob[5:]
    with pytest.raises(WireFormatError, match="invalid packet magic"):
        parse_packet_header(bad_magic)

    bad_crc = bytearray(blob)
    bad_crc[-1] ^= 0x7F
    with pytest.raises(WireFormatError, match="payload CRC mismatch"):
        decode_packet(bytes(bad_crc))


def test_truncation_and_unsupported_version_are_rejected() -> None:
    trajectory = generate_joint_trajectory(num_frames=1024, num_joints=4, seed=910)
    blob = ZPBotCodec(keep_coeffs=8).encode(trajectory)

    with pytest.raises(WireFormatError, match="blob too small for packet header"):
        parse_packet_header(blob[: HEADER_SIZE - 1])

    unsupported = bytearray(blob)
    unsupported[5] = 99
    with pytest.raises(WireFormatError, match="unsupported codec version 99"):
        decode_packet(bytes(unsupported))
