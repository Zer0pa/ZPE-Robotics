from __future__ import annotations

from zpe_robotics.primitives import generate_primitive_corpus
from zpe_robotics.vla_eval import evaluate_token_quality


def test_vla_quality_beats_naive() -> None:
    library, queries = generate_primitive_corpus(seed=2026, library_per_label=30, query_per_label=12, length=80)
    result = evaluate_token_quality(library + queries)

    assert result["delta_vs_naive"] >= 0.0

