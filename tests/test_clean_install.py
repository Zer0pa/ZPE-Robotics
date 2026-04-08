from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_clean_clone_verify_passes(tmp_path) -> None:
    output_path = tmp_path / "clean_clone_verify.json"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/clean_clone_verify.py"), "--repo-root", str(ROOT), "--output", str(output_path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["install_ok"] is True
    assert payload["cli_ok"] is True
    assert payload["tests_ok"] is True
