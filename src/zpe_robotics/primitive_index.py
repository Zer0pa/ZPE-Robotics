"""Primitive-template search over `.zpbot` token streams."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .codec import ZPBotCodec
from .primitives import (
    TEMPLATE_TO_LABEL,
    direction_magnitude_tokens,
    generate_primitive_corpus,
    prototype_pattern,
    shape_signature,
    token_histogram,
)
from .utils import write_json
from .wire import decode_packet


FROZEN_TEMPLATES = ("REACH", "GRASP", "RETRACT", "PLACE", "PUSH")


@dataclass(frozen=True)
class IndexedTrajectory:
    filepath: str
    label: str
    tokens: np.ndarray
    histogram: np.ndarray
    signature: np.ndarray
    suffix_array: tuple[int, ...]


class PrimitiveIndex:
    """O(n) template search across a library of frozen `.zpbot` files."""

    def __init__(self) -> None:
        self._items: list[IndexedTrajectory] = []

    def add(self, filepath: str | Path, label: str) -> None:
        path = Path(filepath)
        trajectory = decode_packet(path.read_bytes())
        reduced = _reduce_trajectory(trajectory)
        tokens = direction_magnitude_tokens(reduced)
        self._items.append(
            IndexedTrajectory(
                filepath=str(path),
                label=str(label),
                tokens=tokens,
                histogram=token_histogram(tokens),
                signature=shape_signature(reduced),
                suffix_array=_build_suffix_array(tokens),
            )
        )

    def search(self, template: str, top_k: int = 10) -> list[tuple[str, str, float, str]]:
        template_name = str(template).upper()
        if template_name not in FROZEN_TEMPLATES:
            raise ValueError(f"unsupported template {template_name}")
        if top_k < 1:
            raise ValueError("top_k must be >= 1")

        query = _template_features(template_name)
        rows: list[tuple[str, str, float, str]] = []
        for item in self._items:
            hist_score = _cosine(item.histogram, query["histogram"])
            shape_score = _cosine(item.signature, query["signature"])
            suffix_score = _best_suffix_overlap(item.tokens, item.suffix_array, query["tokens"])
            score = (0.5 * hist_score) + (0.35 * shape_score) + (0.15 * suffix_score)
            rows.append((item.filepath, item.label, float(score), template_name))

        rows.sort(key=lambda row: row[2], reverse=True)
        return rows[:top_k]


def evaluate_primitive_search(output_dir: str | Path, *, seed: int = 20260243) -> dict[str, Any]:
    root = Path(output_dir)
    corpus_dir = root / "primitive_corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    codec = ZPBotCodec(keep_coeffs=8)
    library, _ = generate_primitive_corpus(seed=seed, library_per_label=60, query_per_label=24, length=96)

    index = PrimitiveIndex()
    for idx, sample in enumerate(library):
        packet_path = corpus_dir / f"{sample.label}_{idx:03d}.zpbot"
        packet_path.write_bytes(codec.encode(sample.trajectory))
        index.add(packet_path, sample.label)

    results = index.search("REACH", top_k=10)
    hits = sum(1 for _, label, _, _ in results if label == "reach")
    precision = float(hits / max(1, len(results)))
    payload = {
        "status": "PASS" if precision >= 0.9 else "FAIL",
        "template": "REACH",
        "precision_at_10": precision,
        "hits": hits,
        "results": [
            {
                "filepath": Path(filepath).name,
                "label": label,
                "score": score,
                "matched_template": matched_template,
            }
            for filepath, label, score, matched_template in results
        ],
    }
    write_json(root / "primitive_search_result.json", payload)
    return payload


def _template_features(template: str) -> dict[str, np.ndarray]:
    label = TEMPLATE_TO_LABEL[template]
    prototype = prototype_pattern(label)
    tokens = direction_magnitude_tokens(prototype)
    return {
        "tokens": tokens,
        "histogram": token_histogram(tokens),
        "signature": shape_signature(prototype),
    }


def _reduce_trajectory(trajectory: np.ndarray) -> np.ndarray:
    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("trajectory must be a 2D array")
    if arr.shape[1] == 1:
        time_axis = np.linspace(0.0, 1.0, arr.shape[0], endpoint=False)
        return np.stack([time_axis, arr[:, 0]], axis=1)
    return arr[:, :2]


def _build_suffix_array(tokens: np.ndarray) -> tuple[int, ...]:
    stream = tuple(int(value) for value in tokens.tolist())
    return tuple(sorted(range(len(stream)), key=lambda idx: stream[idx:]))


def _best_suffix_overlap(tokens: np.ndarray, suffix_array: tuple[int, ...], query_tokens: np.ndarray) -> float:
    token_list = tuple(int(value) for value in tokens.tolist())
    query_list = tuple(int(value) for value in query_tokens.tolist())
    best = 0
    for start in suffix_array:
        overlap = 0
        while (
            overlap < len(query_list)
            and (start + overlap) < len(token_list)
            and token_list[start + overlap] == query_list[overlap]
        ):
            overlap += 1
        if overlap > best:
            best = overlap
    return float(best / max(1, len(query_list)))


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom <= 1.0e-12:
        return 0.0
    return float(np.dot(a, b) / denom)
