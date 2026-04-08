from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_rosbag_demo_benchmark_script_runs(tmp_path) -> None:
    output_path = tmp_path / "rosbag_demo_benchmark.json"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/rosbag_demo_benchmark.py"), "--output", str(output_path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    comparators = payload["comparators"]

    assert payload["dataset"] == "deterministic_rosbag2_demo_fixture"
    assert payload["record_count"] == 12
    assert comparators["zpbot_packet_library"]["compression_ratio"] > comparators["native_mcap"]["compression_ratio"]
    assert comparators["zpbot_packet_library"]["compression_ratio"] > comparators["zstd_l19"]["compression_ratio"]
