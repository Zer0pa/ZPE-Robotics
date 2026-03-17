"""Packet framing helpers for the externalized zpbot-v2 authority surface."""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

import numpy as np

from .constants import (
    AUTHORITY_SURFACE,
    AUTHORITY_WIRE_COMPATIBILITY,
    CODEC_VERSION,
    MAGIC_ZPBOT,
    ZPBOT_HEADER_FORMAT,
)


_HEADER = struct.Struct(ZPBOT_HEADER_FORMAT)
HEADER_SIZE = _HEADER.size


class WireFormatError(ValueError):
    """Raised when a packet blob violates the frozen authority surface."""


@dataclass(frozen=True)
class PacketHeader:
    """Decoded header information for the frozen wire-v1 packet subset."""

    magic: bytes
    wire_version: int
    frames: int
    joints: int
    keep_coeffs: int
    payload_crc32: int
    authority_surface: str = AUTHORITY_SURFACE
    compatibility_mode: str = AUTHORITY_WIRE_COMPATIBILITY

    @property
    def payload_value_count(self) -> int:
        return self.keep_coeffs * self.joints * 2

    @property
    def frequency_bins(self) -> int:
        return (self.frames // 2) + 1


def pack_packet_header(
    frames: int,
    joints: int,
    keep_coeffs: int,
    payload_crc32: int,
    *,
    wire_version: int = CODEC_VERSION,
) -> bytes:
    """Pack the deterministic packet header for the frozen authority subset."""

    _validate_header_fields(frames=frames, joints=joints, keep_coeffs=keep_coeffs)
    return _HEADER.pack(MAGIC_ZPBOT, int(wire_version), int(frames), int(joints), int(keep_coeffs), int(payload_crc32))


def parse_packet_header(blob: bytes, *, allowed_versions: tuple[int, ...] | None = (CODEC_VERSION,)) -> PacketHeader:
    """Parse and validate the packet header without decoding the payload."""

    if len(blob) < HEADER_SIZE:
        raise WireFormatError("blob too small for packet header")

    magic, version, frames, joints, keep_coeffs, payload_crc32 = _HEADER.unpack(blob[:HEADER_SIZE])
    if magic != MAGIC_ZPBOT:
        raise WireFormatError("invalid packet magic")
    if allowed_versions is not None and version not in allowed_versions:
        raise WireFormatError(f"unsupported codec version {version}")

    _validate_header_fields(frames=frames, joints=joints, keep_coeffs=keep_coeffs)

    return PacketHeader(
        magic=magic,
        wire_version=int(version),
        frames=int(frames),
        joints=int(joints),
        keep_coeffs=int(keep_coeffs),
        payload_crc32=int(payload_crc32),
    )


def extract_compressed_payload(
    blob: bytes,
    *,
    allowed_versions: tuple[int, ...] | None = (CODEC_VERSION,),
    validate_crc: bool = True,
) -> tuple[PacketHeader, bytes]:
    """Extract and optionally CRC-check the compressed packet payload."""

    header = parse_packet_header(blob, allowed_versions=allowed_versions)
    compressed_payload = blob[HEADER_SIZE:]
    if validate_crc:
        observed_crc = zlib.crc32(compressed_payload) & 0xFFFFFFFF
        if observed_crc != header.payload_crc32:
            raise WireFormatError("payload CRC mismatch")
    return header, compressed_payload


def decode_packet(blob: bytes, *, allowed_versions: tuple[int, ...] | None = (CODEC_VERSION,)) -> np.ndarray:
    """Decode a deterministic packet blob via the externalized wire contract."""

    header, compressed_payload = extract_compressed_payload(blob, allowed_versions=allowed_versions, validate_crc=True)
    payload = _decompress_payload(compressed_payload)
    values = np.frombuffer(payload, dtype=np.float32)
    if values.size != header.payload_value_count:
        raise WireFormatError("payload size mismatch")

    coeff = values.reshape((header.keep_coeffs, header.joints, 2))
    kept = coeff[..., 0].astype(np.float64) + 1j * coeff[..., 1].astype(np.float64)

    spectrum = np.zeros((header.frequency_bins, header.joints), dtype=np.complex128)
    spectrum[: header.keep_coeffs, :] = kept
    decoded = np.fft.irfft(spectrum, n=header.frames, axis=0)
    return decoded.astype(np.float64)


def describe_packet(blob: bytes, *, allowed_versions: tuple[int, ...] | None = (CODEC_VERSION,)) -> dict[str, object]:
    """Return human-readable packet metadata for authority artifacts."""

    header, compressed_payload = extract_compressed_payload(blob, allowed_versions=allowed_versions, validate_crc=True)
    return {
        "authority_surface": header.authority_surface,
        "compatibility_mode": header.compatibility_mode,
        "wire_version": header.wire_version,
        "frames": header.frames,
        "joints": header.joints,
        "keep_coeffs": header.keep_coeffs,
        "payload_crc32": header.payload_crc32,
        "header_bytes": HEADER_SIZE,
        "payload_bytes": len(compressed_payload),
    }


def _decompress_payload(compressed_payload: bytes) -> bytes:
    try:
        return zlib.decompress(compressed_payload)
    except zlib.error as exc:
        raise WireFormatError(f"decompression failed: {exc}") from exc


def _validate_header_fields(*, frames: int, joints: int, keep_coeffs: int) -> None:
    if int(frames) < 8:
        raise WireFormatError("packet frames must be >= 8")
    if int(joints) < 1:
        raise WireFormatError("packet joints must be >= 1")
    if int(keep_coeffs) < 1:
        raise WireFormatError("packet keep_coeffs must be >= 1")
    max_keep = (int(frames) // 2) + 1
    if int(keep_coeffs) > max_keep:
        raise WireFormatError("packet keep_coeffs exceeds available frequency bins")
