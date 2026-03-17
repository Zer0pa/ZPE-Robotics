from __future__ import annotations

from zpe_robotics.primitive_index import PrimitiveIndex
from zpe_robotics.primitives import generate_primitive_corpus
from zpe_robotics.release_candidate import default_codec


def test_primitive_index_reach_precision_at_10(tmp_path) -> None:
    codec = default_codec()
    library, _ = generate_primitive_corpus(seed=20260243, library_per_label=60, query_per_label=24, length=96)

    index = PrimitiveIndex()
    for idx, sample in enumerate(library):
        packet_path = tmp_path / f"{sample.label}_{idx:03d}.zpbot"
        packet_path.write_bytes(codec.encode(sample.trajectory))
        index.add(packet_path, sample.label)

    results = index.search("REACH", top_k=10)
    hits = sum(1 for _, label, _, _ in results if label == "reach")

    assert len(results) == 10
    assert (hits / 10.0) >= 0.9
