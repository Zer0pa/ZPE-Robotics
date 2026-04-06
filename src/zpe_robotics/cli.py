"""Installable CLI for ZPE-Robotics."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

from . import __version__
from .audit_bundle import generate_audit_bundle
from .anomaly import AnomalyDetector
from .constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY
from .lerobot_codec import ZPELeRobotCodec
from .primitive_index import PrimitiveIndex
from .release_candidate import build_default_bag_record, default_codec
from .rosbag_adapter import decode_records, encode_records
from .utils import sha256_bytes
from .vla_bridge import export_cubicvla_tokens, export_fast_tokens
from .wire import describe_packet, parse_packet_header


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zpe-robotics", description="zpe-robotics CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="encode a single-record deterministic bag into a .zpbot packet")
    encode_parser.add_argument("input_bag", type=Path)
    encode_parser.add_argument("output_zpbot", type=Path)

    decode_parser = subparsers.add_parser("decode", help="decode a .zpbot packet into a single-record deterministic bag")
    decode_parser.add_argument("input_zpbot", type=Path)
    decode_parser.add_argument("output_bag", type=Path)

    verify_parser = subparsers.add_parser("verify", help="verify packet integrity and print CRC plus hash information")
    verify_parser.add_argument("input_zpbot", type=Path)

    info_parser = subparsers.add_parser("info", help="print deterministic packet header fields")
    info_parser.add_argument("input_zpbot", type=Path)

    search_parser = subparsers.add_parser("search", help="search a library of .zpbot files for a primitive template")
    search_parser.add_argument("library_dir", type=Path)
    search_parser.add_argument("template", type=str)

    anomaly_parser = subparsers.add_parser("anomaly", help="fit a fleet model and score a query .zpbot file")
    anomaly_parser.add_argument("fleet_dir", type=Path)
    anomaly_parser.add_argument("query_zpbot", type=Path)

    lerobot_parser = subparsers.add_parser("lerobot-compress", help="compress a LeRobot-style dataset directory")
    lerobot_parser.add_argument("lerobot_dataset_dir", type=Path)
    lerobot_parser.add_argument("output_dir", type=Path)

    export_tokens_parser = subparsers.add_parser("export-tokens", help="export FAST or CubicVLA-compatible tokens")
    export_tokens_parser.add_argument("input_zpbot", type=Path)
    export_tokens_parser.add_argument("--format", choices=("fast", "cubicvla"), required=True)

    audit_bundle_parser = subparsers.add_parser("audit-bundle", help="generate the COMM-03 audit bundle for a .zpbot packet")
    audit_bundle_parser.add_argument("input_zpbot", type=Path)
    audit_bundle_parser.add_argument("output_dir", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "encode":
            return _handle_encode(args.input_bag, args.output_zpbot)
        if args.command == "decode":
            return _handle_decode(args.input_zpbot, args.output_bag)
        if args.command == "verify":
            return _handle_verify(args.input_zpbot)
        if args.command == "info":
            return _handle_info(args.input_zpbot)
        if args.command == "search":
            return _handle_search(args.library_dir, args.template)
        if args.command == "anomaly":
            return _handle_anomaly(args.fleet_dir, args.query_zpbot)
        if args.command == "lerobot-compress":
            return _handle_lerobot_compress(args.lerobot_dataset_dir, args.output_dir)
        if args.command == "export-tokens":
            return _handle_export_tokens(args.input_zpbot, args.format)
        if args.command == "audit-bundle":
            return _handle_audit_bundle(args.input_zpbot, args.output_dir)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"unsupported command: {args.command}", file=sys.stderr)
    return 1


def _handle_encode(input_bag: Path, output_zpbot: Path) -> int:
    codec = default_codec()
    if input_bag.suffix.lower() == ".csv":
        trajectory = _read_csv_trajectory(input_bag)
    else:
        records = decode_records(input_bag.read_bytes(), codec, decode_trajectory=True, strict_index=True)
        if len(records) != 1:
            raise ValueError("encode expects a single-record deterministic bag input")
        trajectory = records[0]["trajectory"]
    output_zpbot.parent.mkdir(parents=True, exist_ok=True)
    output_zpbot.write_bytes(codec.encode(trajectory))
    print(str(output_zpbot))
    return 0


def _handle_decode(input_zpbot: Path, output_bag: Path) -> int:
    codec = default_codec()
    trajectory = codec.decode(input_zpbot.read_bytes())
    output_bag.parent.mkdir(parents=True, exist_ok=True)
    if output_bag.suffix.lower() == ".csv":
        _write_csv_trajectory(output_bag, trajectory)
    else:
        bag_blob = encode_records([build_default_bag_record(trajectory)], codec)
        output_bag.write_bytes(bag_blob)
    print(str(output_bag))
    return 0


def _handle_verify(input_zpbot: Path) -> int:
    payload = _packet_payload(input_zpbot)
    payload["status"] = "PASS"
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _handle_info(input_zpbot: Path) -> int:
    blob = input_zpbot.read_bytes()
    header = parse_packet_header(blob)
    payload = {
        "magic": header.magic.decode("ascii"),
        "version": header.wire_version,
        "frame_count": header.frames,
        "joint_count": header.joints,
        "keep_coeffs": header.keep_coeffs,
        "compression_ratio": round((header.frames * header.joints * 4) / max(1, len(blob)), 6),
        "crc_status": "PASS",
        "authority_surface": header.authority_surface,
        "compatibility_mode": header.compatibility_mode,
        "file": str(input_zpbot),
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _packet_payload(path: Path) -> dict[str, object]:
    blob = path.read_bytes()
    payload = describe_packet(blob)
    payload["file"] = str(path)
    payload["sha256"] = sha256_bytes(blob)
    return payload


def _handle_search(library_dir: Path, template: str) -> int:
    packet_paths = sorted(path for path in library_dir.rglob("*.zpbot") if path.is_file())
    if not packet_paths:
        raise ValueError("search expects at least one .zpbot file in the library directory")

    index = PrimitiveIndex()
    for path in packet_paths:
        label = path.stem.split("_")[0]
        index.add(path, label)

    results = index.search(template, top_k=10)
    payload = [
        {
            "filepath": filepath,
            "label": label,
            "score": round(score, 6),
            "matched_template": matched_template,
        }
        for filepath, label, score, matched_template in results
    ]
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _handle_anomaly(fleet_dir: Path, query_zpbot: Path) -> int:
    packet_paths = sorted(path for path in fleet_dir.rglob("*.zpbot") if path.is_file())
    query_resolved = query_zpbot.resolve()
    train_paths = [path for path in packet_paths if path.resolve() != query_resolved]
    if not train_paths:
        raise ValueError("anomaly expects at least one fleet file excluding the query packet")

    detector = AnomalyDetector(z_threshold=3.0).fit(train_paths)
    report = detector.classify(query_zpbot)
    status = "ANOMALY" if report.flagged else "NORMAL"
    print(f"{status} z_score={report.score:.6f}")
    return 0


def _handle_lerobot_compress(lerobot_dataset_dir: Path, output_dir: Path) -> int:
    report = ZPELeRobotCodec().compress_directory(lerobot_dataset_dir, output_dir)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _handle_export_tokens(input_zpbot: Path, fmt: str) -> int:
    if fmt == "fast":
        tokens = export_fast_tokens(input_zpbot)
        payload = {
            "authority_surface": AUTHORITY_SURFACE,
            "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
            "format": "fast",
            "tokens": tokens.tolist(),
        }
    else:
        payload = export_cubicvla_tokens(input_zpbot)
        payload["format"] = "cubicvla"
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _handle_audit_bundle(input_zpbot: Path, output_dir: Path) -> int:
    payload = generate_audit_bundle(input_zpbot, output_dir)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _read_csv_trajectory(path: Path) -> np.ndarray:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header_consumed = False
        for row in reader:
            if not row:
                continue
            if not header_consumed:
                try:
                    rows.append([float(cell) for cell in row])
                except ValueError:
                    header_consumed = True
                    continue
                header_consumed = True
                continue
            rows.append([float(cell) for cell in row])
    if not rows:
        raise ValueError("CSV trajectory is empty")
    return np.asarray(rows, dtype=np.float64)


def _write_csv_trajectory(path: Path, trajectory: np.ndarray) -> None:
    arr = np.asarray(trajectory, dtype=np.float64)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([f"joint_{idx}" for idx in range(arr.shape[1])])
        writer.writerows(arr.tolist())


if __name__ == "__main__":
    raise SystemExit(main())
