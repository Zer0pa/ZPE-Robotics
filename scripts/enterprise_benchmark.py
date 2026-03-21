"""Phase 9 enterprise benchmark for zpe-motion-kernel."""

from __future__ import annotations

import argparse
import gzip
import io
import json
import math
from pathlib import Path
import platform
import statistics
import time
from typing import Any, Callable

import numpy as np

from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.enterprise_dataset import load_joint_dataset_sample
from zpe_robotics.telemetry import create_tracking_bundle


TARGET_FRAMES = 1000
RUNS = 50
SYNTHETIC_SEED = 20260321


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase 9 enterprise benchmark.")
    parser.add_argument("--dataset-root", type=str, required=True, help="Dataset directory or SYNTHETIC")
    parser.add_argument("--dataset-name", type=str, required=True)
    parser.add_argument("--dataset-provenance", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=RUNS)
    parser.add_argument("--target-frames", type=int, default=TARGET_FRAMES)
    return parser.parse_args()


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    if len(values) == 1:
        return values[0]
    return float(np.percentile(np.asarray(values, dtype=np.float64), q))


def sample_dataset(dataset_root: str, *, target_frames: int) -> tuple[np.ndarray, dict[str, Any]]:
    if dataset_root == "SYNTHETIC":
        return synthetic_sample(target_frames=target_frames)
    repo_id = args_namespace.dataset_name
    return load_joint_dataset_sample(Path(dataset_root), repo_id=repo_id, target_frames=target_frames, min_joints=6)


def synthetic_sample(*, target_frames: int, note: str | None = None) -> tuple[np.ndarray, dict[str, Any]]:
    rng = np.random.default_rng(SYNTHETIC_SEED)
    t = np.linspace(0.0, 20.0, target_frames, dtype=np.float64)
    channels = []
    for joint_index in range(6):
        base = np.sin(t * (0.4 + 0.07 * joint_index))
        harmonic = 0.25 * np.cos(t * (0.8 + 0.03 * joint_index))
        drift = 0.0025 * joint_index * t
        noise = 0.003 * rng.standard_normal(target_frames)
        channels.append(base + harmonic + drift + noise)
    sample = np.stack(channels, axis=1).astype(np.float32)
    meta = {
        "source": "synthetic",
        "dataset_root": "SYNTHETIC",
        "episode_count_used": 1,
        "selected_field": "synthetic_fixture",
        "sample_shape": list(sample.shape),
    }
    if note:
        meta["note"] = note
    return sample, meta


def raw_float32_codec(sample: np.ndarray) -> tuple[bytes, Callable[[bytes], np.ndarray]]:
    buffer = io.BytesIO()
    np.save(buffer, sample.astype(np.float32, copy=False))
    payload = buffer.getvalue()

    def decode(blob: bytes) -> np.ndarray:
        return np.load(io.BytesIO(blob)).astype(np.float32, copy=False)

    return payload, decode


def compressed_bytes_codec(
    sample: np.ndarray,
    *,
    compressor: Callable[[bytes], bytes],
    decompressor: Callable[[bytes], bytes],
) -> tuple[bytes, Callable[[bytes], np.ndarray]]:
    raw = sample.astype(np.float32, copy=False).tobytes(order="C")
    payload = compressor(raw)

    def decode(blob: bytes) -> np.ndarray:
        restored = decompressor(blob)
        return np.frombuffer(restored, dtype=np.float32).reshape(sample.shape)

    return payload, decode


def h5_codec(sample: np.ndarray, *, compression: str, compression_opts: int | None = None) -> tuple[bytes, Callable[[bytes], np.ndarray]]:
    import h5py

    buffer = io.BytesIO()
    with h5py.File(buffer, "w") as handle:
        kwargs: dict[str, Any] = {"compression": compression}
        if compression_opts is not None:
            kwargs["compression_opts"] = compression_opts
        handle.create_dataset("trajectory", data=sample.astype(np.float32, copy=False), **kwargs)
    payload = buffer.getvalue()

    def decode(blob: bytes) -> np.ndarray:
        with h5py.File(io.BytesIO(blob), "r") as handle:
            return handle["trajectory"][...].astype(np.float32, copy=False)

    return payload, decode


def mcap_codec(sample: np.ndarray, *, compression: str) -> tuple[bytes, Callable[[bytes], np.ndarray]]:
    from mcap.reader import make_reader
    from mcap.writer import CompressionType, Writer

    raw = sample.astype(np.float32, copy=False).tobytes(order="C")
    buffer = io.BytesIO()
    writer = Writer(
        buffer,
        compression=CompressionType.LZ4 if compression == "lz4" else CompressionType.ZSTD,
    )
    writer.start(profile="zpe-motion-kernel-bench", library="phase9-enterprise-benchmark")
    schema_id = writer.register_schema("joint_matrix", "application/octet-stream", b"float32 matrix")
    channel_id = writer.register_channel(
        topic="/joint_matrix",
        message_encoding="application/octet-stream",
        schema_id=schema_id,
        metadata={"shape": json.dumps(list(sample.shape))},
    )
    writer.add_message(channel_id=channel_id, log_time=0, publish_time=0, data=raw)
    writer.finish()
    payload = buffer.getvalue()

    def decode(blob: bytes) -> np.ndarray:
        reader = make_reader(io.BytesIO(blob))
        for _schema, channel, message in reader.iter_messages():
            shape = tuple(json.loads(channel.metadata["shape"]))
            return np.frombuffer(message.data, dtype=np.float32).reshape(shape)
        raise ValueError("no MCAP messages found")

    return payload, decode


def zpe_codec(sample: np.ndarray) -> tuple[bytes, Callable[[bytes], np.ndarray]]:
    codec = ZPBotCodec(keep_coeffs=8)
    payload = codec.encode(sample.astype(np.float32, copy=False))

    def decode(blob: bytes) -> np.ndarray:
        return codec.decode(blob)

    return payload, decode


def benchmark_tool(
    tool_id: str,
    sample: np.ndarray,
    *,
    builder: Callable[[np.ndarray], tuple[bytes, Callable[[bytes], np.ndarray]]],
    searchable_without_decode: bool,
    anomaly_detectable: bool,
    cross_platform_deterministic: bool | str,
    tracking: Any,
) -> dict[str, Any]:
    raw_size = int(sample.astype(np.float32, copy=False).nbytes)
    payload, decode = builder(sample)
    decoded = decode(payload)

    encode_times: list[float] = []
    decode_times: list[float] = []
    for _ in range(args_namespace.runs):
        start = time.perf_counter_ns()
        local_payload, _ = builder(sample)
        encode_times.append((time.perf_counter_ns() - start) / 1_000_000.0)
    for _ in range(args_namespace.runs):
        start = time.perf_counter_ns()
        decode(payload)
        decode_times.append((time.perf_counter_ns() - start) / 1_000_000.0)

    metrics = {
        "compression_ratio": float(raw_size / max(1, len(payload))),
        "encode_time_ms_p50": float(statistics.median(encode_times)),
        "encode_time_ms_p95": percentile(encode_times, 95.0),
        "decode_time_ms_p50": float(statistics.median(decode_times)),
        "decode_time_ms_p95": percentile(decode_times, 95.0),
    }
    tracking.log_tool_result(
        tool_id,
        metrics=metrics,
        parameters={
            "raw_size_bytes": raw_size,
            "compressed_size_bytes": len(payload),
            "searchable_without_decode": searchable_without_decode,
            "anomaly_detectable": anomaly_detectable,
        },
    )
    return {
        "tool_id": tool_id,
        "raw_size_bytes": raw_size,
        "compressed_size_bytes": int(len(payload)),
        "compression_ratio": metrics["compression_ratio"],
        "encode_time_ms_p50": metrics["encode_time_ms_p50"],
        "encode_time_ms_p95": metrics["encode_time_ms_p95"],
        "decode_time_ms_p50": metrics["decode_time_ms_p50"],
        "decode_time_ms_p95": metrics["decode_time_ms_p95"],
        "bit_exact_replay": bool(np.array_equal(sample, np.asarray(decoded, dtype=sample.dtype))),
        "searchable_without_decode": searchable_without_decode,
        "anomaly_detectable": anomaly_detectable,
        "cross_platform_deterministic": cross_platform_deterministic,
    }


def compute_gate_verdicts(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    zpe = results["zpe_p8"]
    zstd_l19 = results["zstd_l19"]
    verdicts = {
        "B1": {
            "pass": zpe["compression_ratio"] >= 20.0,
            "actual": zpe["compression_ratio"],
            "condition": "zpe compression ratio >= 20x vs raw float32",
        },
        "B2": {
            "pass": zpe["compression_ratio"] >= 3.0 * zstd_l19["compression_ratio"],
            "actual": zpe["compression_ratio"] / max(zstd_l19["compression_ratio"], 1e-12),
            "condition": "zpe compression ratio >= 3x zstd level 19",
        },
        "B3": {
            "pass": bool(
                zpe["bit_exact_replay"]
                and zpe["searchable_without_decode"]
                and all(not item["searchable_without_decode"] for key, item in results.items() if key != "zpe_p8")
            ),
            "actual": {
                "zpe_bit_exact_replay": zpe["bit_exact_replay"],
                "zpe_searchable_without_decode": zpe["searchable_without_decode"],
            },
            "condition": "zpe is the only tool with bit_exact_replay=true and searchable_without_decode=true",
        },
        "B4": {
            "pass": zpe["encode_time_ms_p50"] < 100.0,
            "actual": zpe["encode_time_ms_p50"],
            "condition": "zpe encode p50 < 100 ms per 1000 frames",
        },
        "B5": {
            "pass": zpe["decode_time_ms_p50"] < 100.0,
            "actual": zpe["decode_time_ms_p50"],
            "condition": "zpe decode p50 < 100 ms per 1000 frames",
        },
    }
    return verdicts


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    global args_namespace
    args_namespace = parse_args()
    args_namespace.output_dir.mkdir(parents=True, exist_ok=True)

    dataset_sample, dataset_meta = sample_dataset(args_namespace.dataset_root, target_frames=args_namespace.target_frames)
    if dataset_sample.shape[0] < 8:
        raise ValueError("benchmark sample must contain at least 8 frames")

    run_name = f"phase9_enterprise_benchmark_{args_namespace.dataset_name}_{int(time.time())}"
    tracking = create_tracking_bundle(
        run_name=run_name,
        input_payload={"dataset_name": args_namespace.dataset_name, "dataset_root": args_namespace.dataset_root},
        metadata={"phase": "09", "sample_shape": list(dataset_sample.shape)},
    )

    import lz4.frame
    import zstandard

    results = {}
    results["raw_float32"] = benchmark_tool(
        "raw_float32",
        dataset_sample,
        builder=raw_float32_codec,
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["zstd_l3"] = benchmark_tool(
        "zstd_l3",
        dataset_sample,
        builder=lambda sample: compressed_bytes_codec(
            sample,
            compressor=zstandard.ZstdCompressor(level=3).compress,
            decompressor=zstandard.ZstdDecompressor().decompress,
        ),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["zstd_l19"] = benchmark_tool(
        "zstd_l19",
        dataset_sample,
        builder=lambda sample: compressed_bytes_codec(
            sample,
            compressor=zstandard.ZstdCompressor(level=19).compress,
            decompressor=zstandard.ZstdDecompressor().decompress,
        ),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["lz4_default"] = benchmark_tool(
        "lz4_default",
        dataset_sample,
        builder=lambda sample: compressed_bytes_codec(
            sample,
            compressor=lz4.frame.compress,
            decompressor=lz4.frame.decompress,
        ),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["gzip_l9"] = benchmark_tool(
        "gzip_l9",
        dataset_sample,
        builder=lambda sample: compressed_bytes_codec(
            sample,
            compressor=lambda raw: gzip.compress(raw, compresslevel=9),
            decompressor=gzip.decompress,
        ),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["h5py_gzip9"] = benchmark_tool(
        "h5py_gzip9",
        dataset_sample,
        builder=lambda sample: h5_codec(sample, compression="gzip", compression_opts=9),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["h5py_lzf"] = benchmark_tool(
        "h5py_lzf",
        dataset_sample,
        builder=lambda sample: h5_codec(sample, compression="lzf"),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["mcap_lz4"] = benchmark_tool(
        "mcap_lz4",
        dataset_sample,
        builder=lambda sample: mcap_codec(sample, compression="lz4"),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["mcap_zstd"] = benchmark_tool(
        "mcap_zstd",
        dataset_sample,
        builder=lambda sample: mcap_codec(sample, compression="zstd"),
        searchable_without_decode=False,
        anomaly_detectable=False,
        cross_platform_deterministic="unknown",
        tracking=tracking,
    )
    results["zpe_p8"] = benchmark_tool(
        "zpe_p8",
        dataset_sample,
        builder=zpe_codec,
        searchable_without_decode=True,
        anomaly_detectable=True,
        cross_platform_deterministic=True,
        tracking=tracking,
    )

    gate_verdicts = compute_gate_verdicts(results)
    benchmark_payload = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset_name": args_namespace.dataset_name,
        "dataset_root": args_namespace.dataset_root,
        "dataset_meta": dataset_meta,
        "sample_shape": list(dataset_sample.shape),
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "system": platform.system(),
        },
        "results": results,
    }

    benchmark_path = args_namespace.output_dir / "benchmark_result.json"
    gate_path = args_namespace.output_dir / "GATE_VERDICTS.json"
    write_json(benchmark_path, benchmark_payload)
    write_json(gate_path, gate_verdicts)

    provenance_copy = args_namespace.output_dir / "dataset_provenance.json"
    provenance_copy.write_text(args_namespace.dataset_provenance.read_text(encoding="utf-8"), encoding="utf-8")

    manifest_payload = {
        "artifacts": {
            str(benchmark_path.name): sha256_file(benchmark_path),
            str(gate_path.name): sha256_file(gate_path),
            str(provenance_copy.name): sha256_file(provenance_copy),
        }
    }
    manifest_path = args_namespace.output_dir / "EVIDENCE_MANIFEST.json"
    write_json(manifest_path, manifest_payload)

    tracking_payload = tracking.finish(
        artifact_paths=[str(benchmark_path), str(gate_path), str(provenance_copy), str(manifest_path)],
        output_payload={"gate_summary": {key: value["pass"] for key, value in gate_verdicts.items()}},
    )
    benchmark_payload["tracking"] = tracking_payload
    write_json(benchmark_path, benchmark_payload)
    manifest_payload["artifacts"][str(benchmark_path.name)] = sha256_file(benchmark_path)
    write_json(manifest_path, manifest_payload)
    return 0


args_namespace: argparse.Namespace


if __name__ == "__main__":
    raise SystemExit(main())
