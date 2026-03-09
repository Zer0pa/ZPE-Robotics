from __future__ import annotations

from zpe_robotics.codec import ZPBotCodec, compression_ratio, joint_rmse_deg
from zpe_robotics.fixtures import generate_joint_trajectory


def test_codec_roundtrip_and_compression() -> None:
    trajectory = generate_joint_trajectory(num_frames=2048, num_joints=6, seed=123)
    codec = ZPBotCodec(keep_coeffs=8, compression_level=9)

    blob = codec.encode(trajectory)
    recon = codec.decode(blob)

    cr = compression_ratio(trajectory, blob)
    rmse = joint_rmse_deg(trajectory, recon)

    assert cr >= 15.0
    assert rmse <= 0.05

