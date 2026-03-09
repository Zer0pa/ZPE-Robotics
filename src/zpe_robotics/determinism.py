"""Determinism replay utilities."""

from __future__ import annotations

from typing import Callable

from .utils import sha256_bytes, stable_json_dumps


def replay_hashes(run_fn: Callable[[], dict], runs: int) -> dict:
    hashes: list[str] = []
    for _ in range(runs):
        payload = run_fn()
        digest = sha256_bytes(stable_json_dumps(payload).encode("utf-8"))
        hashes.append(digest)

    unique = sorted(set(hashes))
    return {
        "runs": runs,
        "hashes": hashes,
        "unique_hash_count": len(unique),
        "unique_hashes": unique,
        "consistent": len(unique) == 1,
    }

