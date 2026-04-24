#!/usr/bin/env python
"""Regression validation for Wave-1 artifact packs."""

from __future__ import annotations

# ruff: noqa: E402

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_robotics.constants import REQUIRED_ARTIFACTS
from zpe_robotics.utils import write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    return parser.parse_args()


def _claims_pass(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("| ROB-C"):
            continue
        if "| FAIL |" in line:
            return False
    return True


def _uncaught_crashes(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"Total uncaught crashes:\s*(\d+)", text)
    if not match:
        return 999
    return int(match.group(1))


def main() -> None:
    args = parse_args()
    root = args.artifacts

    missing = [name for name in REQUIRED_ARTIFACTS if not (root / name).exists()]

    determinism_path = root / "determinism_replay_results.json"
    determinism_consistent = False
    if determinism_path.exists():
        determinism_consistent = bool(json.loads(determinism_path.read_text(encoding="utf-8"))["consistent"])

    claim_pass = _claims_pass(root / "claim_status_delta.md") if (root / "claim_status_delta.md").exists() else False
    uncaught = _uncaught_crashes(root / "falsification_results.md") if (root / "falsification_results.md").exists() else 999

    status = "PASS" if (not missing and determinism_consistent and claim_pass and uncaught == 0) else "FAIL"

    body = "\n".join(
        [
            "Regression Pack",
            f"artifact_root={root}",
            f"missing_count={len(missing)}",
            f"missing={missing}",
            f"determinism_consistent={determinism_consistent}",
            f"claims_pass={claim_pass}",
            f"uncaught_crashes={uncaught}",
            f"status={status}",
            "",
        ]
    )
    write_text(root / "regression_results.txt", body)

    print(json.dumps({"status": status, "missing": missing, "artifact_root": str(root)}, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
