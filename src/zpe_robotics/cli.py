"""Installable CLI for the deterministic motion-kernel release candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .release_candidate import build_default_bag_record, default_codec
from .rosbag_adapter import decode_records, encode_records
from .utils import sha256_bytes
from .wire import describe_packet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zpe", description="ZPE motion-kernel release-candidate CLI")
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
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"unsupported command: {args.command}", file=sys.stderr)
    return 1


def _handle_encode(input_bag: Path, output_zpbot: Path) -> int:
    codec = default_codec()
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
    bag_blob = encode_records([build_default_bag_record(trajectory)], codec)
    output_bag.parent.mkdir(parents=True, exist_ok=True)
    output_bag.write_bytes(bag_blob)
    print(str(output_bag))
    return 0


def _handle_verify(input_zpbot: Path) -> int:
    payload = _packet_payload(input_zpbot)
    payload["status"] = "PASS"
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _handle_info(input_zpbot: Path) -> int:
    payload = _packet_payload(input_zpbot)
    payload.pop("sha256", None)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _packet_payload(path: Path) -> dict[str, object]:
    blob = path.read_bytes()
    payload = describe_packet(blob)
    payload["file"] = str(path)
    payload["sha256"] = sha256_bytes(blob)
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
