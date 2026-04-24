"""Helpers for multi-dataset LeRobot benchmark sweeps."""

from __future__ import annotations

import statistics
import time
from typing import Any


PRIMARY_LEROBOT_DATASETS = (
    "lerobot/columbia_cairlab_pusht_real",
    "IPEC-COMMUNITY/bridge_orig_lerobot",
    "IPEC-COMMUNITY/droid_lerobot",
    "IPEC-COMMUNITY/language_table_lerobot",
    "lerobot/aloha_mobile_shrimp",
    "lerobot/umi_cup_in_the_wild",
)

FALLBACK_LEROBOT_DATASETS = (
    "IPEC-COMMUNITY/fractal20220817_data_lerobot",
)

CURATED_LEROBOT_DATASETS = PRIMARY_LEROBOT_DATASETS + FALLBACK_LEROBOT_DATASETS


def dataset_slug(repo_id: str) -> str:
    return repo_id.lower().replace("/", "__").replace("-", "_")


def dataset_family(repo_id: str) -> str:
    lower = repo_id.lower()
    if "aloha" in lower:
        return "aloha"
    if "pusht" in lower:
        return "pusht"
    if "xarm" in lower:
        return "xarm"
    if "umi" in lower:
        return "umi"
    if "language_table" in lower:
        return "language-table"
    if "droid" in lower:
        return "droid"
    if "bridge" in lower:
        return "bridge"
    if "fractal" in lower:
        return "fractal"
    return dataset_slug(repo_id).split("__")[-1]


def build_dataset_index_payload() -> dict[str, Any]:
    return {
        "primary_candidates": list(PRIMARY_LEROBOT_DATASETS),
        "fallback_candidates": list(FALLBACK_LEROBOT_DATASETS),
        "substitution_policy": (
            "Attempt primary candidates first. Preserve every acquisition and qualification miss in "
            "dataset_manifest.json. Use fallback datasets only to reach at least three qualified "
            "benchmarks spanning at least two materially distinct dataset families."
        ),
        "selection_floor": {
            "min_qualified_datasets": 3,
            "min_materially_distinct_families": 2,
        },
    }


def build_dataset_rollup(
    repo_id: str,
    *,
    benchmark_result: dict[str, Any],
    gate_verdicts: dict[str, Any],
    phase9_anchor: dict[str, Any],
    benchmark_dir: str,
) -> dict[str, Any]:
    zpe = benchmark_result["results"]["zpe_p8"]
    compression_ratio = float(zpe["compression_ratio"])
    issues: list[str] = []
    if compression_ratio < phase9_anchor["compression_ratio"]:
        issues.append("compression ratio is below the Phase 9 real-data anchor")
    if not bool(zpe["bit_exact_replay"]):
        issues.append("bit_exact replay remains false on this dataset")
    if not bool(gate_verdicts["B3"]["pass"]):
        issues.append("B3 remains open on this dataset")

    return {
        "repo_id": repo_id,
        "family": dataset_family(repo_id),
        "dataset_name": benchmark_result["dataset_name"],
        "sample_shape": benchmark_result["sample_shape"],
        "benchmark_dir": benchmark_dir,
        "compression_ratio": compression_ratio,
        "encode_time_ms_p50": float(zpe["encode_time_ms_p50"]),
        "decode_time_ms_p50": float(zpe["decode_time_ms_p50"]),
        "bit_exact_replay": bool(zpe["bit_exact_replay"]),
        "max_abs_error": float(zpe.get("max_abs_error", 0.0)),
        "gate_summary": {gate_id: bool(payload["pass"]) for gate_id, payload in gate_verdicts.items()},
        "regression_callouts": issues,
    }


def build_benchmark_spread_summary(
    dataset_rollups: list[dict[str, Any]],
    *,
    phase9_anchor: dict[str, Any],
    min_qualified: int,
    min_families: int,
) -> dict[str, Any]:
    families = sorted({item["family"] for item in dataset_rollups})
    ratios = [float(item["compression_ratio"]) for item in dataset_rollups]
    encodes = [float(item["encode_time_ms_p50"]) for item in dataset_rollups]
    decodes = [float(item["decode_time_ms_p50"]) for item in dataset_rollups]

    if dataset_rollups:
        spread = {
            "compression_ratio": {
                "min": min(ratios),
                "median": statistics.median(ratios),
                "max": max(ratios),
            },
            "encode_time_ms_p50": {
                "min": min(encodes),
                "median": statistics.median(encodes),
                "max": max(encodes),
            },
            "decode_time_ms_p50": {
                "min": min(decodes),
                "median": statistics.median(decodes),
                "max": max(decodes),
            },
        }
    else:
        spread = {}

    acceptance_pass = len(dataset_rollups) >= min_qualified and len(families) >= min_families

    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "PASS" if acceptance_pass else "FAIL",
        "benchmarked_dataset_count": len(dataset_rollups),
        "materially_distinct_families": families,
        "requirements": {
            "min_qualified_datasets": min_qualified,
            "min_materially_distinct_families": min_families,
        },
        "phase9_anchor": phase9_anchor,
        "zpe_p8_spread": spread,
        "datasets": dataset_rollups,
        "regression_callouts": [
            {
                "repo_id": item["repo_id"],
                "issues": item["regression_callouts"],
            }
            for item in dataset_rollups
            if item["regression_callouts"]
        ],
        "non_claims": [
            "Benchmark breadth does not close B3.",
            "Benchmark breadth does not close attack 3.",
            "Benchmark breadth does not create a general anomaly-readiness claim.",
            "Benchmark breadth does not add a robotics Rust ABI.",
        ],
    }
