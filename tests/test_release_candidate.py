from __future__ import annotations

import numpy as np

from zpe_robotics.codec import joint_rmse_deg
from zpe_robotics.release_candidate import (
    REFERENCE_ROUNDTRIP_SHA256,
    build_single_packet_composition,
    compute_reference_bridge_roundtrip,
    decode_single_packet_bag,
)


def test_reference_bridge_hash_matches_frozen_anchor() -> None:
    report = compute_reference_bridge_roundtrip()

    assert report["bit_consistent"]
    assert report["original_sha256"] == REFERENCE_ROUNDTRIP_SHA256
    assert report["replay_sha256"] == REFERENCE_ROUNDTRIP_SHA256


def test_single_packet_composition_roundtrip_preserves_shape_and_rmse() -> None:
    composition = build_single_packet_composition()
    decoded = decode_single_packet_bag(composition.bag_blob)

    assert decoded.shape == composition.trajectory.shape
    assert joint_rmse_deg(composition.trajectory, decoded) <= 0.05
    assert not np.array_equal(decoded, composition.trajectory)
