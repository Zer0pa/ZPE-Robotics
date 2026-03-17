from __future__ import annotations

import numpy as np

from zpe_robotics.release_candidate import build_canonical_arm_fixture, default_codec
from zpe_robotics.vla_bridge import evaluate_fast_token_accuracy, export_fast_tokens


def test_vla_bridge_exports_fast_tokens_and_meets_accuracy_gate(tmp_path) -> None:
    trajectory = build_canonical_arm_fixture()
    packet_path = tmp_path / "arm_fixture.zpbot"
    packet_path.write_bytes(default_codec().encode(trajectory))

    tokens = export_fast_tokens(packet_path)
    report = evaluate_fast_token_accuracy()

    assert tokens.shape == trajectory.shape
    assert tokens.dtype == np.int32
    assert int(tokens.min()) >= 0
    assert int(tokens.max()) <= 23
    assert report["token_accuracy"] >= 0.808
