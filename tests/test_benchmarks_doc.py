from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_benchmarks_doc_has_methodology_and_anchor_table() -> None:
    text = (ROOT / "BENCHMARKS.md").read_text(encoding="utf-8")

    assert "# Benchmarks" in text
    assert "## Methodology" in text
    assert "## Reproduction Commands" in text
    assert "| dataset | baseline | ZPE | ratio | improvement |" in text
    assert "`lerobot/columbia_cairlab_pusht_real`" in text
