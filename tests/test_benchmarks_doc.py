from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_benchmarks_doc_has_methodology_and_anchor_table() -> None:
    text = (ROOT / "BENCHMARKS.md").read_text(encoding="utf-8")

    assert "# Benchmarks" in text
    assert "## Methodology" in text
    assert "## Reproduction Commands" in text
    assert "| dataset | baseline | ZPE | ratio | improvement |" in text
    assert "`lerobot/columbia_cairlab_pusht_real`" in text


def test_benchmarks_doc_matches_checked_in_artifacts() -> None:
    text = (ROOT / "BENCHMARKS.md").read_text(encoding="utf-8")
    lerobot_root = ROOT / "proofs/artifacts/lerobot_expanded_benchmarks"

    for slug in [
        "lerobot__columbia_cairlab_pusht_real",
        "lerobot__aloha_mobile_shrimp",
        "lerobot__umi_cup_in_the_wild",
    ]:
        payload = json.loads((lerobot_root / slug / "benchmark_result.json").read_text(encoding="utf-8"))
        dataset = payload["dataset_name"]
        results = payload["results"]
        assert f"| `{dataset}` | `zstd_l19 {results['zstd_l19']['compression_ratio']:.2f}x` | `zpe_p8 {results['zpe_p8']['compression_ratio']:.2f}x` | `{results['zpe_p8']['compression_ratio']:.2f}x` |" in text

    rosbag = json.loads((ROOT / "proofs/artifacts/benchmarks/rosbag_demo_benchmark.json").read_text(encoding="utf-8"))
    comparators = rosbag["comparators"]
    assert (
        f"| `{rosbag['dataset']}` | `native_mcap {comparators['native_mcap']['compression_ratio']:.2f}x` | "
        f"`zpbot_packet_library {comparators['zpbot_packet_library']['compression_ratio']:.2f}x` | "
        f"`{comparators['zpbot_packet_library']['compression_ratio']:.2f}x` |"
    ) in text
