#!/usr/bin/env python3
"""Benchmark the current core artifact paths for Phase 8 refinement decisions."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from zpe_robotics.audit_bundle import build_provenance_manifest, generate_audit_bundle
from zpe_robotics.release_candidate import default_codec
from zpe_robotics.wire import describe_packet


BenchmarkFn = Callable[[], object]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark core Phase 8 artifact paths")
    parser.add_argument("packet", type=Path, help="Path to canonical .zpbot packet")
    parser.add_argument("output", type=Path, help="Path to JSON output")
    parser.add_argument("--fast-iterations", type=int, default=200, help="Iterations for encode/decode/describe")
    parser.add_argument("--slow-iterations", type=int, default=20, help="Iterations for manifest and audit bundle")
    return parser


def _time_function(fn: BenchmarkFn, iterations: int) -> dict[str, Any]:
    samples_ms: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter()
        fn()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        samples_ms.append(elapsed_ms)

    ordered = sorted(samples_ms)
    p95_index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return {
        "iterations": iterations,
        "median_ms": round(statistics.median(ordered), 6),
        "mean_ms": round(statistics.fmean(ordered), 6),
        "min_ms": round(min(ordered), 6),
        "max_ms": round(max(ordered), 6),
        "p95_ms": round(ordered[p95_index], 6),
    }


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    packet_path = args.packet.resolve()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    packet = packet_path.read_bytes()
    packet_info = describe_packet(packet)
    codec = default_codec()
    trajectory = codec.decode(packet)

    def run_describe() -> object:
        return describe_packet(packet)

    def run_decode() -> object:
        return codec.decode(packet)

    def run_encode() -> object:
        return codec.encode(trajectory)

    def run_manifest() -> object:
        return build_provenance_manifest(packet_path)

    def run_audit_bundle() -> object:
        with tempfile.TemporaryDirectory(prefix="phase8_audit_") as tmpdir:
            return generate_audit_bundle(packet_path, tmpdir)

    benchmarks = {
        "describe_packet": _time_function(run_describe, args.fast_iterations),
        "decode_packet": _time_function(run_decode, args.fast_iterations),
        "encode_packet": _time_function(run_encode, args.fast_iterations),
        "build_provenance_manifest": _time_function(run_manifest, args.slow_iterations),
        "generate_audit_bundle": _time_function(run_audit_bundle, args.slow_iterations),
    }

    ranked = sorted(
        (
            {
                "name": name,
                "median_ms": result["median_ms"],
                "p95_ms": result["p95_ms"],
            }
            for name, result in benchmarks.items()
        ),
        key=lambda item: item["median_ms"],
        reverse=True,
    )

    payload = {
        "status": "PASS",
        "phase": "08",
        "packet_path": str(packet_path),
        "packet_bytes": len(packet),
        "packet_info": packet_info,
        "decoded_shape": list(trajectory.shape),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "benchmarks": benchmarks,
        "ranked_by_median_ms": ranked,
    }

    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
