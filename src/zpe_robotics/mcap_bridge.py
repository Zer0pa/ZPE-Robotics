"""MCAP-aligned bridge envelope for opaque zpbot payload transport.

This module is intentionally honest: it preserves MCAP-style schema/channel/message
semantics in a deterministic envelope, but it does not claim to emit byte-for-byte
official MCAP files.
"""

from __future__ import annotations

import json
import struct
import zlib
from dataclasses import dataclass
from typing import Any

from .codec import ZPBotCodec
from .constants import (
    AUTHORITY_SURFACE,
    AUTHORITY_WIRE_COMPATIBILITY,
    DEFAULT_TRAJECTORY_TOPIC,
    MCAP_BRIDGE_HEADER_FORMAT,
    MCAP_BRIDGE_MAGIC,
    MCAP_BRIDGE_MESSAGE_ENCODING,
    MCAP_BRIDGE_PROFILE,
    MCAP_BRIDGE_SCHEMA_ENCODING,
    MCAP_BRIDGE_SCHEMA_NAME,
)
from .rosbag_adapter import BagFormatError, RoundtripResult, decode_trajectory_blob, normalize_records
from .utils import sha256_bytes, stable_json_dumps


_HEADER = struct.Struct(MCAP_BRIDGE_HEADER_FORMAT)


class BridgeFormatError(ValueError):
    """Raised when the MCAP-aligned bridge envelope is malformed."""


@dataclass(frozen=True)
class BridgeSchema:
    schema_id: int
    name: str
    encoding: str
    data_json: dict[str, Any]


def encode_bridge_records(
    records: list[dict[str, Any]],
    codec: ZPBotCodec,
    *,
    topic: str | None = None,
) -> bytes:
    """Encode deterministic records into the MCAP-aligned bridge envelope."""

    try:
        normalized_records = normalize_records(records, codec)
    except BagFormatError as exc:
        raise BridgeFormatError(str(exc)) from exc

    bridge_topic = topic or _infer_topic(normalized_records)
    schema = BridgeSchema(
        schema_id=1,
        name=MCAP_BRIDGE_SCHEMA_NAME,
        encoding=MCAP_BRIDGE_SCHEMA_ENCODING,
        data_json={
            "authority_surface": AUTHORITY_SURFACE,
            "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
            "payload_encoding": MCAP_BRIDGE_MESSAGE_ENCODING,
        },
    )
    channel = {
        "id": 1,
        "schema_id": schema.schema_id,
        "topic": bridge_topic,
        "message_encoding": MCAP_BRIDGE_MESSAGE_ENCODING,
        "metadata": {
            "authority_surface": AUTHORITY_SURFACE,
            "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        },
    }
    messages = []
    for record in normalized_records:
        messages.append(
            {
                "sequence": int(record["index"]),
                "channel_id": channel["id"],
                "log_time_ns": int(record["timestamp_ns"]),
                "publish_time_ns": int(record["timestamp_ns"]),
                "data_b64": record["trajectory_blob_b64"],
                "metadata": {
                    "robot": record["robot"],
                    "joint_names": list(record["joint_names"]),
                    "quality": float(record["quality"]),
                    "topic": record["topic"],
                    "encoding": record["encoding"],
                },
            }
        )

    envelope = {
        "profile": MCAP_BRIDGE_PROFILE,
        "schemas": [
            {
                "id": schema.schema_id,
                "name": schema.name,
                "encoding": schema.encoding,
                "data_json": schema.data_json,
            }
        ],
        "channels": [channel],
        "messages": messages,
    }
    return _build_bridge_blob(envelope)


def decode_bridge_records(
    bridge_blob: bytes,
    codec: ZPBotCodec,
    *,
    decode_trajectory: bool = False,
    strict_sequence: bool = True,
) -> list[dict[str, Any]]:
    """Decode the MCAP-aligned bridge envelope back into deterministic records."""

    envelope = _decode_envelope(bridge_blob)
    if envelope.get("profile") != MCAP_BRIDGE_PROFILE:
        raise BridgeFormatError("unexpected bridge profile")

    schemas = envelope.get("schemas", [])
    channels = envelope.get("channels", [])
    messages = envelope.get("messages", [])
    if len(schemas) != 1 or len(channels) != 1:
        raise BridgeFormatError("bridge envelope expects exactly one schema and one channel")

    schema = schemas[0]
    channel = channels[0]
    if schema.get("encoding") != MCAP_BRIDGE_SCHEMA_ENCODING:
        raise BridgeFormatError("unexpected bridge schema encoding")
    if channel.get("message_encoding") != MCAP_BRIDGE_MESSAGE_ENCODING:
        raise BridgeFormatError("unexpected bridge message encoding")

    out: list[dict[str, Any]] = []
    for expected_seq, message in enumerate(messages):
        sequence = int(message["sequence"])
        if strict_sequence and sequence != expected_seq:
            raise BridgeFormatError("bridge message sequence violation")

        metadata = message.get("metadata", {})
        record = {
            "index": sequence,
            "topic": str(metadata.get("topic", channel["topic"])),
            "timestamp_ns": int(message["publish_time_ns"]),
            "robot": str(metadata.get("robot", "unknown_robot")),
            "joint_names": [str(name) for name in metadata.get("joint_names", [])],
            "quality": float(metadata.get("quality", 1.0)),
            "encoding": str(metadata.get("encoding", MCAP_BRIDGE_MESSAGE_ENCODING)),
            "trajectory_blob_b64": str(message["data_b64"]),
        }
        if record["encoding"] != MCAP_BRIDGE_MESSAGE_ENCODING:
            raise BridgeFormatError(f"unsupported bridge message encoding {record['encoding']}")
        if decode_trajectory:
            record["trajectory"] = decode_trajectory_blob(record["trajectory_blob_b64"], codec)
        out.append(record)

    return out


def evaluate_bridge_roundtrip(records: list[dict[str, Any]], codec: ZPBotCodec) -> RoundtripResult:
    original = encode_bridge_records(records, codec)
    decoded = decode_bridge_records(original, codec, decode_trajectory=False, strict_sequence=True)
    replay = encode_bridge_records(decoded, codec)

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


def resequence_blob(blob: bytes) -> bytes:
    envelope = _decode_envelope(blob)
    messages = list(envelope.get("messages", []))
    if len(messages) < 2:
        return blob
    messages[0], messages[1] = messages[1], messages[0]
    envelope["messages"] = messages
    return _build_bridge_blob(envelope)


def _decode_envelope(blob: bytes) -> dict[str, Any]:
    if len(blob) < _HEADER.size:
        raise BridgeFormatError("bridge blob too small")

    magic, payload_len, expected_crc = _HEADER.unpack(blob[: _HEADER.size])
    if magic != MCAP_BRIDGE_MAGIC:
        raise BridgeFormatError("invalid bridge magic")

    payload = blob[_HEADER.size :]
    if len(payload) != payload_len:
        raise BridgeFormatError("bridge payload length mismatch")

    observed_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if observed_crc != expected_crc:
        raise BridgeFormatError("bridge CRC mismatch")

    return json.loads(payload.decode("utf-8"))


def _build_bridge_blob(envelope: dict[str, Any]) -> bytes:
    payload = stable_json_dumps(envelope).encode("utf-8")
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    return _HEADER.pack(MCAP_BRIDGE_MAGIC, len(payload), crc) + payload


def _infer_topic(records: list[dict[str, Any]]) -> str:
    if not records:
        return DEFAULT_TRAJECTORY_TOPIC
    return str(records[0].get("topic", DEFAULT_TRAJECTORY_TOPIC))
