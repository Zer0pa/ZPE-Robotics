from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from zpe_robotics.enterprise_dataset import load_episode_matrices
from zpe_robotics.lerobot_codec import ZPELeRobotCodec, dump_episode_json


ROOT = Path(__file__).resolve().parents[1]


def test_real_lerobot_roundtrip_when_enabled(tmp_path) -> None:
    if os.environ.get("ZPE_RUN_REAL_LEROBOT") != "1":
        pytest.skip("set ZPE_RUN_REAL_LEROBOT=1 to run bounded real-data roundtrip")

    pytest.importorskip("huggingface_hub")
    pytest.importorskip("pyarrow")

    data_root = tmp_path / "data"
    provenance_path = tmp_path / "provenance.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/acquire_enterprise_dataset.py"),
            "--repo-id",
            "lerobot/columbia_cairlab_pusht_real",
            "--data-root",
            str(data_root),
            "--output",
            str(provenance_path),
            "--include-namespace",
            "--require-real",
            "--max-parquet-files",
            "1",
            "--max-total-bytes",
            "200000000",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout

    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    selected = provenance["selected"]
    dataset_root = Path(selected["path"])
    episodes, meta = load_episode_matrices(dataset_root, repo_id="lerobot/columbia_cairlab_pusht_real", min_joints=6)
    assert episodes

    dataset_dir = tmp_path / "episodes"
    dataset_dir.mkdir()
    episode = np.asarray(episodes[0], dtype=np.float32)
    fps = float(meta.get("fps") or 1.0)
    dump_episode_json(
        dataset_dir / "episode_000.json",
        {
            "joint_positions": episode,
            "timestamps": np.arange(episode.shape[0], dtype=np.float64) / fps,
            "episode_metadata": {"repo_id": "lerobot/columbia_cairlab_pusht_real"},
        },
    )

    output_dir = tmp_path / "compressed"
    report = ZPELeRobotCodec().compress_directory(dataset_dir, output_dir)
    packet_path = next(output_dir.rglob("*.zpbot"))
    decoded = ZPELeRobotCodec().decode_episode(packet_path)

    assert report["files_processed"] == 1
    assert np.allclose(decoded["joint_positions"], episode, atol=1.0e-5)
