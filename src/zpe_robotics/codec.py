"""Deterministic spectral `.zpbot` codec implementation."""

from __future__ import annotations

import zlib
from dataclasses import dataclass

import numpy as np

from .wire import WireFormatError, decode_packet, pack_packet_header


class CodecError(ValueError):
    """Raised when codec payloads are malformed."""


@dataclass(frozen=True)
class ZPBotCodec:
    """Frequency-domain trajectory codec with deterministic framing."""

    keep_coeffs: int = 8
    compression_level: int = 9

    def encode(self, trajectory: np.ndarray) -> bytes:
        arr = _validate_trajectory(trajectory)
        frames, joints = arr.shape
        freq_bins = (frames // 2) + 1
        keep = int(min(max(1, self.keep_coeffs), freq_bins))

        spectrum = np.fft.rfft(arr, axis=0)
        kept = spectrum[:keep, :]
        payload = np.empty((keep, joints, 2), dtype=np.float32)
        payload[..., 0] = kept.real.astype(np.float32)
        payload[..., 1] = kept.imag.astype(np.float32)

        compressed_payload = zlib.compress(payload.tobytes(order="C"), level=self.compression_level)
        crc = zlib.crc32(compressed_payload) & 0xFFFFFFFF

        header = pack_packet_header(frames, joints, keep, crc)
        return header + compressed_payload

    def decode(self, blob: bytes) -> np.ndarray:
        try:
            return decode_packet(blob)
        except WireFormatError as exc:
            raise CodecError(str(exc)) from exc


def compression_ratio(trajectory: np.ndarray, encoded_blob: bytes, raw_dtype: np.dtype = np.float32) -> float:
    arr = _validate_trajectory(trajectory)
    raw_bytes = arr.astype(raw_dtype, copy=False).nbytes
    if raw_bytes == 0:
        raise ValueError("raw byte count is zero")
    return float(raw_bytes / max(1, len(encoded_blob)))


def joint_rmse_deg(reference: np.ndarray, reconstructed: np.ndarray) -> float:
    ref = _validate_trajectory(reference)
    rec = _validate_trajectory(reconstructed)
    if ref.shape != rec.shape:
        raise ValueError("shape mismatch between reference and reconstructed")
    diff = np.rad2deg(ref - rec)
    return float(np.sqrt(np.mean(np.square(diff))))


def _validate_trajectory(trajectory: np.ndarray) -> np.ndarray:
    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("trajectory must be a 2D array [frames, joints]")
    if arr.shape[0] < 8:
        raise ValueError("trajectory must include at least 8 frames")
    if arr.shape[1] < 1:
        raise ValueError("trajectory must include at least 1 joint")
    if not np.isfinite(arr).all():
        raise ValueError("trajectory contains non-finite values")
    return arr
