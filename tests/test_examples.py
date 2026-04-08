from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _run_example(relative_path: str, *args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(ROOT / relative_path), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def test_lerobot_compress_example_runs_with_fixture(tmp_path) -> None:
    payload = _run_example("examples/lerobot_compress.py", "--output-dir", str(tmp_path / "lerobot"))

    assert payload["mode"] == "fixture"
    assert payload["files_processed"] == 1
    assert payload["packet_count"] == 1
    assert float(payload["compression_ratio"]) > 1.0


def test_rosbag_bridge_example_runs(tmp_path) -> None:
    payload = _run_example("examples/rosbag_bridge.py", "--output-dir", str(tmp_path / "rosbag"))

    assert payload["array_close"] is True
    assert payload["bit_consistent"] is False
    assert payload["records"] == 1
    assert float(payload["compression_ratio"]) > 1.0


def test_mcap_bridge_example_runs(tmp_path) -> None:
    payload = _run_example("examples/mcap_bridge.py", "--output-dir", str(tmp_path / "mcap"))

    assert payload["bit_consistent"] is True
    assert payload["records"] == 12
    assert payload["search_without_decode"]["hits"] == 12


def test_examples_readme_mentions_download_and_run_commands() -> None:
    text = (ROOT / "examples/README.md").read_text(encoding="utf-8")

    assert "python scripts/acquire_enterprise_dataset.py" in text
    assert "python examples/lerobot_compress.py" in text
    assert "python examples/rosbag_bridge.py" in text
    assert "python examples/mcap_bridge.py" in text
