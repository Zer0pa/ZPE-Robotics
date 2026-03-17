from __future__ import annotations

import numpy as np

from zpe_robotics.lerobot_codec import ZPELeRobotCodec, build_synthetic_episode


def test_lerobot_codec_roundtrip_and_compression_gate(tmp_path) -> None:
    codec = ZPELeRobotCodec()
    episode = build_synthetic_episode(frames=100, joints=6, hz=50.0)
    packet_path = tmp_path / "episode.zpbot"

    artifacts = codec.encode_episode(episode, packet_path)
    decoded = codec.decode_episode(packet_path)

    expected = np.asarray(episode["joint_positions"], dtype=np.float32)
    observed = np.asarray(decoded["joint_positions"], dtype=np.float32)

    assert np.allclose(observed, expected, atol=1.0e-5)
    assert packet_path.stat().st_size < (0.05 * expected.nbytes)
    assert artifacts.compression_ratio > 20.0
    assert decoded["provenance"]["authority_surface"] == "zpbot-v2"
    assert decoded["provenance"]["compatibility_mode"] == "wire-v1"
    assert decoded["provenance"]["codec_version"] == 1
    assert decoded["provenance"]["generation_timestamp"]
