"""LeRobot-compatible episode compression over frozen `.zpbot` packets."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .codec import ZPBotCodec, compression_ratio
from .constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY, CODEC_VERSION
from .utils import ensure_dir, write_json
from .wire import describe_packet


METADATA_SUFFIX = ".meta.json"


@dataclass(frozen=True)
class EpisodeArtifacts:
    packet_path: Path
    metadata_path: Path
    compression_ratio: float


class ZPELeRobotCodec:
    """Encode and decode LeRobot-style episode dictionaries."""

    def __init__(self, codec: ZPBotCodec | None = None) -> None:
        self.codec = codec or ZPBotCodec(keep_coeffs=4)

    def encode_episode(self, episode: dict[str, Any], output_path: str | Path) -> EpisodeArtifacts:
        output = Path(output_path)
        positions, timestamps, user_metadata, structure = _normalize_episode(episode)
        output.parent.mkdir(parents=True, exist_ok=True)

        blob = self.codec.encode(positions)
        output.write_bytes(blob)

        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        provenance = {
            "authority_surface": AUTHORITY_SURFACE,
            "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
            "codec_version": CODEC_VERSION,
            "generation_timestamp": timestamp,
        }
        sidecar = {
            "structure": structure,
            "timestamps": timestamps.tolist(),
            "episode_metadata": user_metadata,
            "provenance": provenance,
            "packet_info": describe_packet(blob),
            "compression_ratio": compression_ratio(positions, blob),
        }
        metadata_path = _metadata_path(output)
        write_json(metadata_path, sidecar)
        return EpisodeArtifacts(
            packet_path=output,
            metadata_path=metadata_path,
            compression_ratio=float(sidecar["compression_ratio"]),
        )

    def decode_episode(self, input_path: str | Path) -> dict[str, Any]:
        packet_path = Path(input_path)
        packet = packet_path.read_bytes()
        positions = self.codec.decode(packet).astype(np.float32)
        sidecar = _load_sidecar(packet_path)
        timestamps = np.asarray(sidecar.get("timestamps", np.arange(positions.shape[0], dtype=np.float64)), dtype=np.float64)
        episode_metadata = dict(sidecar.get("episode_metadata", {}))
        provenance = dict(
            sidecar.get(
                "provenance",
                {
                    "authority_surface": AUTHORITY_SURFACE,
                    "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
                    "codec_version": CODEC_VERSION,
                    "generation_timestamp": dt.datetime.fromtimestamp(packet_path.stat().st_mtime, tz=dt.timezone.utc).isoformat(),
                },
            )
        )
        structure = str(sidecar.get("structure", "top_level"))

        if structure == "observation":
            return {
                "observation": {"joint_positions": positions},
                "timestamps": timestamps,
                "episode_metadata": episode_metadata,
                "provenance": provenance,
            }

        return {
            "joint_positions": positions,
            "timestamps": timestamps,
            "episode_metadata": episode_metadata,
            "provenance": provenance,
        }

    def compress_directory(self, dataset_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
        src = Path(dataset_dir)
        dst = Path(output_dir)
        ensure_dir(dst)

        episode_paths = sorted(
            [path for path in src.rglob("*") if path.suffix.lower() in {".json", ".npz"}]
        )
        if not episode_paths:
            raise ValueError("no supported episode files found in dataset directory")

        results = []
        raw_total = 0
        compressed_total = 0
        for path in episode_paths:
            episode = load_episode_file(path)
            rel = path.relative_to(src)
            target = (dst / rel).with_suffix(".zpbot")
            artifacts = self.encode_episode(episode, target)
            positions, _, _, _ = _normalize_episode(episode)
            raw_total += positions.astype(np.float32, copy=False).nbytes
            compressed_total += artifacts.packet_path.stat().st_size
            results.append(
                {
                    "source": str(path),
                    "target": str(artifacts.packet_path),
                    "compression_ratio": artifacts.compression_ratio,
                }
            )

        overall_ratio = float(raw_total / max(1, compressed_total))
        return {
            "files_processed": len(results),
            "raw_bytes": raw_total,
            "compressed_bytes": compressed_total,
            "compression_ratio": overall_ratio,
            "results": results,
        }


def load_episode_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if file_path.suffix.lower() == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return _episode_from_json_payload(payload)
    if file_path.suffix.lower() == ".npz":
        archive = np.load(file_path, allow_pickle=True)
        episode_metadata = {}
        if "episode_metadata_json" in archive:
            episode_metadata = json.loads(str(archive["episode_metadata_json"].item()))
        return {
            "joint_positions": np.asarray(archive["joint_positions"], dtype=np.float32),
            "timestamps": np.asarray(archive["timestamps"], dtype=np.float64),
            "episode_metadata": episode_metadata,
        }
    raise ValueError(f"unsupported episode file: {file_path}")


def dump_episode_json(path: str | Path, episode: dict[str, Any]) -> None:
    positions, timestamps, episode_metadata, structure = _normalize_episode(episode)
    payload: dict[str, Any]
    if structure == "observation":
        payload = {
            "observation": {"joint_positions": positions.astype(np.float32).tolist()},
            "timestamps": timestamps.tolist(),
            "episode_metadata": episode_metadata,
        }
    else:
        payload = {
            "joint_positions": positions.astype(np.float32).tolist(),
            "timestamps": timestamps.tolist(),
            "episode_metadata": episode_metadata,
        }
    target = Path(path)
    ensure_dir(target.parent)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def build_synthetic_episode(frames: int = 100, joints: int = 6, hz: float = 50.0) -> dict[str, Any]:
    t = np.arange(frames, dtype=np.float64) / float(hz)
    shared_wave = 0.2 * np.sin(2.0 * np.pi * t)
    positions = np.repeat(shared_wave[:, None], joints, axis=1).astype(np.float32)
    return {
        "joint_positions": positions,
        "timestamps": t,
        "episode_metadata": {
            "robot": "wave1_arm",
            "frequency_hz": hz,
        },
    }


def evaluate_lerobot_roundtrip(output_dir: str | Path) -> dict[str, Any]:
    codec = ZPELeRobotCodec()
    episode = build_synthetic_episode()
    packet_path = Path(output_dir) / "lerobot_episode.zpbot"
    artifacts = codec.encode_episode(episode, packet_path)
    decoded = codec.decode_episode(packet_path)
    recon = np.asarray(decoded["joint_positions"], dtype=np.float32)
    ref = np.asarray(episode["joint_positions"], dtype=np.float32)
    max_abs_error = float(np.max(np.abs(ref - recon)))
    return {
        "status": "PASS" if max_abs_error <= 1.0e-5 else "FAIL",
        "compression_ratio": artifacts.compression_ratio,
        "max_abs_error": max_abs_error,
        "authority_surface": decoded["provenance"]["authority_surface"],
        "compatibility_mode": decoded["provenance"]["compatibility_mode"],
        "generation_timestamp": decoded["provenance"]["generation_timestamp"],
    }


def _normalize_episode(episode: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, dict[str, Any], str]:
    if "joint_positions" in episode:
        structure = "top_level"
        positions = np.asarray(episode["joint_positions"], dtype=np.float32)
    elif isinstance(episode.get("observation"), dict) and "joint_positions" in episode["observation"]:
        structure = "observation"
        positions = np.asarray(episode["observation"]["joint_positions"], dtype=np.float32)
    else:
        raise ValueError("episode must contain joint_positions or observation.joint_positions")

    if positions.ndim != 2:
        raise ValueError("episode joint_positions must be [frames, joints]")

    timestamps = np.asarray(
        episode.get("timestamps", np.arange(positions.shape[0], dtype=np.float64)),
        dtype=np.float64,
    )
    if timestamps.ndim != 1 or timestamps.shape[0] != positions.shape[0]:
        raise ValueError("timestamps must be a 1D array aligned with joint_positions")

    episode_metadata = dict(episode.get("episode_metadata", episode.get("metadata", {})))
    return positions.astype(np.float64), timestamps, episode_metadata, structure


def _episode_from_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    episode: dict[str, Any] = {}
    if "observation" in payload and isinstance(payload["observation"], dict):
        episode["observation"] = {
            "joint_positions": np.asarray(payload["observation"]["joint_positions"], dtype=np.float32)
        }
    else:
        episode["joint_positions"] = np.asarray(payload["joint_positions"], dtype=np.float32)
    episode["timestamps"] = np.asarray(payload.get("timestamps", []), dtype=np.float64)
    episode["episode_metadata"] = dict(payload.get("episode_metadata", {}))
    return episode


def _metadata_path(packet_path: Path) -> Path:
    return packet_path.with_name(packet_path.name + METADATA_SUFFIX)


def _load_sidecar(packet_path: Path) -> dict[str, Any]:
    metadata_path = _metadata_path(packet_path)
    if not metadata_path.exists():
        return {}
    return json.loads(metadata_path.read_text(encoding="utf-8"))
