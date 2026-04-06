from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"

# The benchmark sweep helpers live in scripts/ and are intentionally not part
# of the importable package surface. These tests load them directly without
# requiring network or optional benchmark dependencies.
sys.path.insert(0, str(SCRIPTS_DIR))

import acquire_enterprise_dataset  # noqa: E402
import lerobot_benchmark_sweep  # noqa: E402
from zpe_robotics.enterprise_dataset import qualify_dataset  # noqa: E402


def test_sanitize_repo_id_is_filesystem_safe() -> None:
    slug = acquire_enterprise_dataset._sanitize_repo_id("IPEC-COMMUNITY/droid_lerobot")  # noqa: SLF001
    assert "/" not in slug
    assert slug


def test_partial_download_plan_respects_parquet_limit_and_byte_cap() -> None:
    repo_files = [
        {"path": "meta/info.json", "size": 10},
        {"path": "data/part-000.parquet", "size": 100},
        {"path": "data/part-001.parquet", "size": 200},
        {"path": "data/part-002.parquet", "size": 300},
        {"path": "README.md", "size": 999},
    ]
    plan = acquire_enterprise_dataset._select_partial_download_files(  # noqa: SLF001
        repo_files,
        max_parquet_files=2,
        max_total_bytes=250,
    )
    planned_paths = [item["path"] for item in plan["planned_files"]]

    assert "meta/info.json" in planned_paths
    assert planned_paths.count("meta/info.json") == 1
    assert sum(path.endswith(".parquet") for path in planned_paths) <= 2
    assert plan["planned_total_bytes"] <= 250
    assert "data/part-000.parquet" in planned_paths
    assert "data/part-001.parquet" not in planned_paths


def test_spread_reports_min_median_max() -> None:
    spread = lerobot_benchmark_sweep._spread([3.0, 1.0, 2.0])  # noqa: SLF001
    assert spread == {"min": 1.0, "median": 2.0, "max": 3.0}


def test_extract_zpe_tool_metrics_contains_required_fields() -> None:
    payload = {
        "dataset_name": "demo",
        "dataset_meta": {
            "repo_id": "demo",
            "sample_shape": [1000, 8],
            "selected_field": "observation.state",
            "joint_count": 8,
            "fps": 10.0,
            "episode_count_total": 2,
            "frame_count_total": 2000,
            "is_real_dataset": True,
            "qualified_reason": "QUALIFIED",
            "dataset_root": "/workspace/data/demo",
        },
        "results": {
            "zpe_p8": {
                "compression_ratio": 123.0,
                "encode_time_ms_p50": 0.1,
                "decode_time_ms_p50": 0.2,
                "bit_exact_replay": False,
                "max_abs_error": 0.0001,
            }
        },
    }
    summary = lerobot_benchmark_sweep._extract_zpe_tool_metrics(payload)  # noqa: SLF001

    assert summary["compression_ratio"] == 123.0
    assert summary["encode_time_ms_p50"] == 0.1
    assert summary["decode_time_ms_p50"] == 0.2
    assert summary["bit_exact_replay"] is False
    assert summary["max_abs_error"] == 0.0001
    assert summary["sample_shape"] == [1000, 8]
    assert summary["dataset_meta"]["selected_field"] == "observation.state"


def test_real_dataset_heuristic_covers_phase10_priority_ids(tmp_path) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir(parents=True)

    real_roots = [
        "IPEC-COMMUNITY/droid_lerobot",
        "IPEC-COMMUNITY/language_table_lerobot",
        "IPEC-COMMUNITY/bridge_orig_lerobot",
        "IPEC-COMMUNITY/fractal20220817_data_lerobot",
        "lerobot/aloha_mobile_shrimp",
        "lerobot/umi_cup_in_the_wild",
        "lerobot/columbia_cairlab_pusht_real",
    ]

    for repo_id in real_roots:
        qualification = qualify_dataset(
            dataset_root,
            repo_id=repo_id,
            min_joints=6,
            require_real=False,
        )
        assert qualification.is_real is True, repo_id

    sim_qualification = qualify_dataset(
        dataset_root,
        repo_id="lerobot/aloha_sim_transfer_cube_scripted",
        min_joints=6,
        require_real=False,
    )
    assert sim_qualification.is_real is False
