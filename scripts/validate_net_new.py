#!/usr/bin/env python
"""Validate Appendix E NET-NEW artifacts and impracticality contract."""

from __future__ import annotations

# ruff: noqa: E402

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_robotics.constants import ALLOWED_IMP_CODES, APPENDIX_E_ARTIFACTS, RUNPOD_DEFERMENT_ARTIFACTS
from zpe_robotics.utils import write_text


REQ_KEYS = {"resource", "code", "command", "error_signature", "fallback", "claim_impact_note"}
GAP_STATUS_ALLOWED = {"RESOLVED", "FAIL", "PAUSED_EXTERNAL"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.artifacts

    missing = [name for name in APPENDIX_E_ARTIFACTS if not (root / name).exists()]

    imp_path = root / "impracticality_decisions.json"
    imp_records = []
    bad_imp = []
    if imp_path.exists():
        payload = json.loads(imp_path.read_text(encoding="utf-8"))
        imp_records = payload.get("records", [])
        for idx, rec in enumerate(imp_records):
            missing_keys = sorted(list(REQ_KEYS - set(rec)))
            if missing_keys:
                bad_imp.append(f"record_{idx}_missing_keys={missing_keys}")
                continue
            if rec.get("code") not in ALLOWED_IMP_CODES:
                bad_imp.append(f"record_{idx}_invalid_code={rec.get('code')}")

    requires_runpod = any(rec.get("code") == "IMP-COMPUTE" for rec in imp_records)
    runpod_missing = []
    if requires_runpod:
        runpod_missing = [name for name in RUNPOD_DEFERMENT_ARTIFACTS if not (root / name).exists()]

    claim_map_path = root / "max_claim_resource_map.json"
    claim_map_ok = False
    if claim_map_path.exists():
        payload = json.loads(claim_map_path.read_text(encoding="utf-8"))
        claim_map = payload.get("claim_map", {})
        required_claims = {f"ROB-C00{i}" for i in range(1, 9)}
        claim_map_ok = required_claims.issubset(set(claim_map))

    gap_path = root / "net_new_gap_closure_matrix.json"
    bad_gaps = []
    if gap_path.exists():
        payload = json.loads(gap_path.read_text(encoding="utf-8"))
        for idx, gap in enumerate(payload.get("gaps", [])):
            status_value = gap.get("status")
            if status_value not in GAP_STATUS_ALLOWED:
                bad_gaps.append(f"gap_{idx}_invalid_status={status_value}")
            if gap.get("attempted") is not True:
                bad_gaps.append(f"gap_{idx}_attempted_not_true")
    else:
        bad_gaps.append("missing_net_new_gap_closure_matrix")

    status = "PASS"
    if missing or bad_imp or runpod_missing or (not claim_map_ok) or bad_gaps:
        status = "FAIL"

    body = "\n".join(
        [
            "NET-NEW Validation",
            f"artifact_root={root}",
            f"missing={missing}",
            f"bad_impracticality={bad_imp}",
            f"requires_runpod={requires_runpod}",
            f"runpod_missing={runpod_missing}",
            f"claim_map_ok={claim_map_ok}",
            f"bad_gaps={bad_gaps}",
            f"status={status}",
            "",
        ]
    )
    write_text(root / "max_resource_validation_status.txt", body)

    print(
        json.dumps(
            {
                "status": status,
                "missing": missing,
                "bad_impracticality": bad_imp,
                "runpod_missing": runpod_missing,
                "claim_map_ok": claim_map_ok,
                "bad_gaps": bad_gaps,
            },
            indent=2,
        )
    )

    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
