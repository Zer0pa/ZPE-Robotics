"""Deterministic rosbag2-style adapter with bit-consistent roundtrip checks."""

from __future__ import annotations

import base64
import json
import struct
import zlib
from dataclasses import dataclass
from typing import Any

import numpy as np

from .codec import ZPBotCodec
from .utils import sha256_bytes, stable_json_dumps


_BAG_MAGIC = b"ZPBAG1"
_HEADER = struct.Struct("<6sII")


class BagFormatError(ValueError):
    """Raised when bag payload is malformed or corrupted."""


@dataclass(frozen=True)
class RoundtripResult:
    bit_consistent: bool
    original_sha256: str
    replay_sha256: str
    bytes_equal: bool
    records: int


def encode_records(records: list[dict[str, Any]], codec: ZPBotCodec) -> bytes:
    encoded_records: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        item: dict[str, Any] = {
            "index": int(record.get("index", idx)),
            "topic": str(record["topic"]),
            "timestamp_ns": int(record["timestamp_ns"]),
            "robot": str(record.get("robot", "unknown_robot")),
            "joint_names": [str(name) for name in record.get("joint_names", [])],
            "quality": float(record.get("quality", 1.0)),
            "encoding": "zpbot",
        }

        if "trajectory_blob_b64" in record:
            item["trajectory_blob_b64"] = str(record["trajectory_blob_b64"])
        else:
            trajectory = np.asarray(record["trajectory"], dtype=np.float64)
            blob = codec.encode(trajectory)
            item["trajectory_blob_b64"] = base64.b64encode(blob).decode("ascii")

        encoded_records.append(item)

    envelope = {
        "schema": "zpe_rosbag_wave1",
        "schema_version": 1,
        "records": encoded_records,
    }

    payload = stable_json_dumps(envelope).encode("utf-8")
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    header = _HEADER.pack(_BAG_MAGIC, len(payload), crc)
    return header + payload


def decode_records(
    bag_blob: bytes,
    codec: ZPBotCodec,
    decode_trajectory: bool = False,
    strict_index: bool = True,
) -> list[dict[str, Any]]:
    if len(bag_blob) < _HEADER.size:
        raise BagFormatError("bag blob too small")

    magic, payload_len, expected_crc = _HEADER.unpack(bag_blob[: _HEADER.size])
    if magic != _BAG_MAGIC:
        raise BagFormatError("invalid bag magic")

    payload = bag_blob[_HEADER.size :]
    if len(payload) != payload_len:
        raise BagFormatError("payload length mismatch")

    observed_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if observed_crc != expected_crc:
        raise BagFormatError("bag CRC mismatch")

    envelope = json.loads(payload.decode("utf-8"))
    records = envelope.get("records", [])
    out: list[dict[str, Any]] = []

    for expected_idx, rec in enumerate(records):
        rec_idx = int(rec["index"])
        if strict_index and rec_idx != expected_idx:
            raise BagFormatError("record index order violation")

        decoded: dict[str, Any] = {
            "index": rec_idx,
            "topic": rec["topic"],
            "timestamp_ns": int(rec["timestamp_ns"]),
            "robot": rec["robot"],
            "joint_names": list(rec.get("joint_names", [])),
            "quality": float(rec.get("quality", 1.0)),
            "trajectory_blob_b64": rec["trajectory_blob_b64"],
        }

        if decode_trajectory:
            blob = base64.b64decode(rec["trajectory_blob_b64"].encode("ascii"))
            decoded["trajectory"] = codec.decode(blob)

        out.append(decoded)

    return out


def evaluate_roundtrip(records: list[dict[str, Any]], codec: ZPBotCodec) -> RoundtripResult:
    original = encode_records(records, codec)
    decoded = decode_records(original, codec, decode_trajectory=False, strict_index=True)
    replay = encode_records(decoded, codec)

    original_hash = sha256_bytes(original)
    replay_hash = sha256_bytes(replay)

    bytes_equal = original == replay
    return RoundtripResult(
        bit_consistent=bool(bytes_equal and (original_hash == replay_hash)),
        original_sha256=original_hash,
        replay_sha256=replay_hash,
        bytes_equal=bytes_equal,
        records=len(records),
    )


def corrupt_blob(blob: bytes) -> bytes:
    if len(blob) <= _HEADER.size + 4:
        raise ValueError("blob too small to corrupt")
    tampered = bytearray(blob)
    tampered[_HEADER.size + 3] ^= 0x7F
    return bytes(tampered)


def reorder_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(records) < 2:
        return records
    swapped = list(records)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    return swapped

