"""Deterministic rosbag2-style adapter with bit-consistent roundtrip checks."""

from __future__ import annotations

import base64
from io import BytesIO
import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .codec import ZPBotCodec
from .constants import (
    AUTHORITY_SURFACE,
    AUTHORITY_WIRE_COMPATIBILITY,
    MCAP_MAGIC,
    ZPBAG_LEGACY_VERSION,
    ZPBAG_HEADER_FORMAT,
    ZPBAG_MAGIC,
    ZPBAG_NATIVE_INDEX_NAME,
    ZPBAG_NATIVE_MESSAGE_ENCODING,
    ZPBAG_NATIVE_PROFILE,
    ZPBAG_NATIVE_SCHEMA_ENCODING,
    ZPBAG_NATIVE_VERSION,
    ZPBAG_SCHEMA_NAME,
    ZPBAG_SCHEMA_VERSION,
    ZPBOT_MESSAGE_ENCODING,
)
from .utils import sha256_bytes, stable_json_dumps


_HEADER = struct.Struct(ZPBAG_HEADER_FORMAT)


class BagFormatError(ValueError):
    """Raised when bag payload is malformed or corrupted."""


@dataclass(frozen=True)
class RoundtripResult:
    bit_consistent: bool
    original_sha256: str
    replay_sha256: str
    bytes_equal: bool
    records: int
    version: str = ZPBAG_LEGACY_VERSION
    canonical_bridge_sha256: str = ""


def normalize_record(record: dict[str, Any], idx: int, codec: ZPBotCodec) -> dict[str, Any]:
    """Normalize a raw record into the deterministic transport shape."""

    item: dict[str, Any] = {
        "index": int(record.get("index", idx)),
        "topic": str(record["topic"]),
        "timestamp_ns": int(record["timestamp_ns"]),
        "robot": str(record.get("robot", "unknown_robot")),
        "joint_names": [str(name) for name in record.get("joint_names", [])],
        "quality": float(record.get("quality", 1.0)),
        "encoding": str(record.get("encoding", ZPBOT_MESSAGE_ENCODING)),
    }
    if item["encoding"] != ZPBOT_MESSAGE_ENCODING:
        raise BagFormatError(f"unsupported record encoding {item['encoding']}")

    if "trajectory_blob_b64" in record:
        item["trajectory_blob_b64"] = str(record["trajectory_blob_b64"])
        return item

    if "trajectory" not in record:
        raise BagFormatError("record missing trajectory")

    trajectory = np.asarray(record["trajectory"], dtype=np.float64)
    blob = codec.encode(trajectory)
    item["trajectory_blob_b64"] = base64.b64encode(blob).decode("ascii")
    return item


def normalize_records(records: list[dict[str, Any]], codec: ZPBotCodec) -> list[dict[str, Any]]:
    return [normalize_record(record, idx, codec) for idx, record in enumerate(records)]


def decode_trajectory_blob(blob_b64: str, codec: ZPBotCodec) -> np.ndarray:
    blob = base64.b64decode(blob_b64.encode("ascii"))
    return codec.decode(blob)


def encode_records(
    records: list[dict[str, Any]],
    codec: ZPBotCodec,
    *,
    version: str = ZPBAG_LEGACY_VERSION,
) -> bytes:
    encoded_records = normalize_records(records, codec)
    if version == ZPBAG_LEGACY_VERSION:
        return _encode_legacy_records(encoded_records)
    if version == ZPBAG_NATIVE_VERSION:
        return _encode_native_records(encoded_records)
    raise BagFormatError(f"unsupported bag version {version}")


def _encode_legacy_records(encoded_records: list[dict[str, Any]]) -> bytes:
    envelope = {
        "schema": ZPBAG_SCHEMA_NAME,
        "schema_version": ZPBAG_SCHEMA_VERSION,
        "records": encoded_records,
    }

    payload = stable_json_dumps(envelope).encode("utf-8")
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    header = _HEADER.pack(ZPBAG_MAGIC, len(payload), crc)
    return header + payload


def decode_records(
    bag_blob: bytes,
    codec: ZPBotCodec,
    decode_trajectory: bool = False,
    strict_index: bool = True,
    version: str | None = None,
) -> list[dict[str, Any]]:
    detected_version = version or detect_bag_version(bag_blob)
    if detected_version == ZPBAG_LEGACY_VERSION:
        return _decode_legacy_records(
            bag_blob,
            codec,
            decode_trajectory=decode_trajectory,
            strict_index=strict_index,
        )
    if detected_version == ZPBAG_NATIVE_VERSION:
        return _decode_native_records(
            bag_blob,
            codec,
            decode_trajectory=decode_trajectory,
            strict_index=strict_index,
        )
    raise BagFormatError(f"unsupported bag version {detected_version}")


def _decode_legacy_records(
    bag_blob: bytes,
    codec: ZPBotCodec,
    *,
    decode_trajectory: bool,
    strict_index: bool,
) -> list[dict[str, Any]]:
    if len(bag_blob) < _HEADER.size:
        raise BagFormatError("bag blob too small")

    magic, payload_len, expected_crc = _HEADER.unpack(bag_blob[: _HEADER.size])
    if magic != ZPBAG_MAGIC:
        raise BagFormatError("invalid bag magic")

    payload = bag_blob[_HEADER.size :]
    if len(payload) != payload_len:
        raise BagFormatError("payload length mismatch")

    observed_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if observed_crc != expected_crc:
        raise BagFormatError("bag CRC mismatch")

    envelope = json.loads(payload.decode("utf-8"))
    if envelope.get("schema") != ZPBAG_SCHEMA_NAME:
        raise BagFormatError("unexpected bag schema")
    if int(envelope.get("schema_version", -1)) != ZPBAG_SCHEMA_VERSION:
        raise BagFormatError("unexpected bag schema version")

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
            "encoding": str(rec.get("encoding", ZPBOT_MESSAGE_ENCODING)),
            "trajectory_blob_b64": rec["trajectory_blob_b64"],
        }
        if decoded["encoding"] != ZPBOT_MESSAGE_ENCODING:
            raise BagFormatError(f"unsupported record encoding {decoded['encoding']}")

        if decode_trajectory:
            decoded["trajectory"] = decode_trajectory_blob(decoded["trajectory_blob_b64"], codec)

        out.append(decoded)

    return out


def evaluate_roundtrip(
    records: list[dict[str, Any]],
    codec: ZPBotCodec,
    *,
    version: str = ZPBAG_LEGACY_VERSION,
) -> RoundtripResult:
    original = encode_records(records, codec, version=version)
    decoded = decode_records(original, codec, decode_trajectory=False, strict_index=True, version=version)
    replay = encode_records(decoded, codec, version=version)

    original_hash = sha256_bytes(original)
    replay_hash = sha256_bytes(replay)

    bytes_equal = original == replay
    canonical_bridge_sha256 = ""
    if version == ZPBAG_NATIVE_VERSION:
        canonical_bridge_sha256 = bridge_roundtrip_sha256(decoded, codec)
    return RoundtripResult(
        bit_consistent=bool(bytes_equal and (original_hash == replay_hash)),
        original_sha256=original_hash,
        replay_sha256=replay_hash,
        bytes_equal=bytes_equal,
        records=len(records),
        version=version,
        canonical_bridge_sha256=canonical_bridge_sha256,
    )


def corrupt_blob(blob: bytes) -> bytes:
    version = detect_bag_version(blob)
    if version == ZPBAG_NATIVE_VERSION:
        if len(blob) <= 16:
            raise ValueError("blob too small to corrupt")
        tampered = bytearray(blob)
        tampered[15] ^= 0x7F
        return bytes(tampered)
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


def detect_bag_version(bag_blob: bytes) -> str:
    if bag_blob.startswith(ZPBAG_MAGIC):
        return ZPBAG_LEGACY_VERSION
    if bag_blob.startswith(MCAP_MAGIC):
        return ZPBAG_NATIVE_VERSION
    raise BagFormatError("unsupported bag magic")


def bridge_roundtrip_sha256(records: list[dict[str, Any]], codec: ZPBotCodec) -> str:
    from .mcap_bridge import encode_bridge_records

    return sha256_bytes(encode_bridge_records(records, codec))


def bag_info(bag_blob: bytes, codec: ZPBotCodec) -> dict[str, Any]:
    version = detect_bag_version(bag_blob)
    records = decode_records(bag_blob, codec, decode_trajectory=False, strict_index=False, version=version)
    payload = {
        "version": version,
        "records": len(records),
        "sha256": sha256_bytes(bag_blob),
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
    }
    if version == ZPBAG_NATIVE_VERSION:
        payload["canonical_bridge_sha256"] = bridge_roundtrip_sha256(records, codec)
    return payload


def read_mcap_native_index(path: str | Path) -> dict[str, Any]:
    return _read_native_index(Path(path).read_bytes())


def _encode_native_records(encoded_records: list[dict[str, Any]]) -> bytes:
    from mcap.writer import Writer

    buffer = BytesIO()
    writer = Writer(buffer)
    writer.start(profile=ZPBAG_NATIVE_PROFILE, library="python mcap 1.3.1")
    schema_id = writer.register_schema(
        name=ZPBAG_SCHEMA_NAME,
        encoding=ZPBAG_NATIVE_SCHEMA_ENCODING,
        data=stable_json_dumps(
            {
                "authority_surface": AUTHORITY_SURFACE,
                "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
                "payload_encoding": ZPBOT_MESSAGE_ENCODING,
                "version": ZPBAG_NATIVE_VERSION,
            }
        ).encode("utf-8"),
    )

    channel_ids: dict[str, int] = {}
    record_index: list[dict[str, Any]] = []
    for record in encoded_records:
        topic = str(record["topic"])
        channel_id = channel_ids.get(topic)
        if channel_id is None:
            channel_id = writer.register_channel(
                topic=topic,
                message_encoding=ZPBAG_NATIVE_MESSAGE_ENCODING,
                schema_id=schema_id,
                metadata={
                    "authority_surface": AUTHORITY_SURFACE,
                    "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
                    "version": ZPBAG_NATIVE_VERSION,
                },
            )
            channel_ids[topic] = channel_id

        payload = base64.b64decode(str(record["trajectory_blob_b64"]).encode("ascii"))
        writer.add_message(
            channel_id=channel_id,
            log_time=int(record["timestamp_ns"]),
            publish_time=int(record["timestamp_ns"]),
            sequence=int(record["index"]),
            data=payload,
        )
        record_index.append(
            {
                "index": int(record["index"]),
                "channel_id": channel_id,
                "topic": topic,
                "timestamp_ns": int(record["timestamp_ns"]),
                "robot": str(record["robot"]),
                "joint_names": list(record.get("joint_names", [])),
                "quality": float(record.get("quality", 1.0)),
                "encoding": str(record.get("encoding", ZPBOT_MESSAGE_ENCODING)),
            }
        )

    writer.add_metadata(
        ZPBAG_NATIVE_INDEX_NAME,
        {
            "authority_surface": AUTHORITY_SURFACE,
            "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
            "version": ZPBAG_NATIVE_VERSION,
            "records_json": stable_json_dumps(record_index),
        },
    )
    writer.finish()
    return buffer.getvalue()


def _decode_native_records(
    bag_blob: bytes,
    codec: ZPBotCodec,
    *,
    decode_trajectory: bool,
    strict_index: bool,
) -> list[dict[str, Any]]:
    from mcap.reader import make_reader

    reader = make_reader(BytesIO(bag_blob), validate_crcs=True)
    record_index = _read_native_index(bag_blob)
    metadata_by_key = {
        (int(item["channel_id"]), int(item["index"])): item
        for item in record_index.get("records", [])
    }

    out: list[dict[str, Any]] = []
    for expected_idx, (schema, channel, message) in enumerate(reader.iter_messages()):
        if strict_index and int(message.sequence) != expected_idx:
            raise BagFormatError("record index order violation")
        if schema is None or schema.encoding != ZPBAG_NATIVE_SCHEMA_ENCODING:
            raise BagFormatError("unexpected native schema encoding")
        if channel.message_encoding != ZPBAG_NATIVE_MESSAGE_ENCODING:
            raise BagFormatError("unexpected native message encoding")

        record_meta = metadata_by_key.get((int(channel.id), int(message.sequence)), {})
        decoded: dict[str, Any] = {
            "index": int(message.sequence),
            "topic": str(record_meta.get("topic", channel.topic)),
            "timestamp_ns": int(record_meta.get("timestamp_ns", message.publish_time)),
            "robot": str(record_meta.get("robot", "unknown_robot")),
            "joint_names": [str(name) for name in record_meta.get("joint_names", [])],
            "quality": float(record_meta.get("quality", 1.0)),
            "encoding": str(record_meta.get("encoding", ZPBOT_MESSAGE_ENCODING)),
            "trajectory_blob_b64": base64.b64encode(bytes(message.data)).decode("ascii"),
        }
        if decoded["encoding"] != ZPBOT_MESSAGE_ENCODING:
            raise BagFormatError(f"unsupported record encoding {decoded['encoding']}")
        if decode_trajectory:
            decoded["trajectory"] = codec.decode(bytes(message.data))
        out.append(decoded)

    return out


def _read_native_index(bag_blob: bytes) -> dict[str, Any]:
    from mcap.reader import make_reader

    reader = make_reader(BytesIO(bag_blob), validate_crcs=True)
    for metadata in reader.iter_metadata():
        if metadata.name != ZPBAG_NATIVE_INDEX_NAME:
            continue
        payload = dict(metadata.metadata)
        records_json = payload.get("records_json", "[]")
        try:
            records = json.loads(records_json)
        except json.JSONDecodeError as exc:
            raise BagFormatError("native record index is malformed") from exc
        return {
            "authority_surface": payload.get("authority_surface", AUTHORITY_SURFACE),
            "compatibility_mode": payload.get("compatibility_mode", AUTHORITY_WIRE_COMPATIBILITY),
            "version": payload.get("version", ZPBAG_NATIVE_VERSION),
            "records": records,
        }
    raise BagFormatError("native record index missing")
