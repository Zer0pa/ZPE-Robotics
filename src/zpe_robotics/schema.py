"""Multi-demo movement schema primitives."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import numpy as np


SCHEMA_VERSION = "movement-schema-v1"


class SchemaError(ValueError):
    """Raised when movement schema inputs or packets are invalid."""


@dataclass(frozen=True)
class DemoMetadata:
    """Metadata carried with one movement demonstration."""

    action_label: str
    episode_id: str
    embodiment: str = "unknown"
    source_path: str = ""
    feature_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class SchemaMetadata:
    """Configuration for fitting a movement schema."""

    action_label: str
    frame_count: int = 128
    component_count: int = 8
    feature_names: tuple[str, ...] = ()
    canonicalization: str = "start_relative_resampled_v1"


@dataclass(frozen=True)
class CanonicalMovement:
    """A phase-normalized movement array with feature labels."""

    values: np.ndarray
    feature_names: tuple[str, ...]
    frame_count: int


@dataclass(frozen=True)
class SchemaCode:
    """Latent schema code for one movement attempt."""

    latent: np.ndarray
    residual_rmse: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "latent": self.latent.astype(float).tolist(),
            "residual_rmse": float(self.residual_rmse),
        }


@dataclass(frozen=True)
class SchemaScore:
    """Distance breakdown for a movement attempt against a schema."""

    distance: float
    latent_distance: float
    reconstruction_rmse: float
    endpoint_error: float
    residual_rmse: float

    def to_dict(self) -> dict[str, float]:
        return {
            "distance": float(self.distance),
            "latent_distance": float(self.latent_distance),
            "reconstruction_rmse": float(self.reconstruction_rmse),
            "endpoint_error": float(self.endpoint_error),
            "residual_rmse": float(self.residual_rmse),
        }


@dataclass(frozen=True)
class MovementSchemaV1:
    """Action-conditioned movement-form schema fitted from repeated demos."""

    metadata: SchemaMetadata
    central_form: np.ndarray
    components: np.ndarray
    latent_mean: np.ndarray
    latent_variance: np.ndarray
    feature_offset: np.ndarray
    feature_scale: np.ndarray
    reconstruction_rmse_mean: float
    demo_count: int

    @classmethod
    def fit(
        cls,
        demonstrations: list[np.ndarray],
        metadata: SchemaMetadata,
    ) -> "MovementSchemaV1":
        if len(demonstrations) < 2:
            raise SchemaError("MovementSchemaV1 requires at least two demonstrations")

        canonical = [
            canonicalize_trajectory(
                demo,
                frame_count=metadata.frame_count,
                feature_names=metadata.feature_names,
            ).values
            for demo in demonstrations
        ]
        stack = np.stack(canonical, axis=0)
        feature_offset = np.mean(stack, axis=(0, 1))
        feature_scale = np.std(stack, axis=(0, 1))
        feature_scale = np.where(feature_scale < 1.0e-8, 1.0, feature_scale)
        normalized = (stack - feature_offset) / feature_scale

        flat = normalized.reshape(normalized.shape[0], -1)
        central_flat = np.mean(flat, axis=0)
        centered = flat - central_flat
        components = _fit_components(centered, metadata.component_count)
        latents = centered @ components.T

        latent_mean = np.mean(latents, axis=0)
        latent_variance = np.var(latents, axis=0, ddof=1) if len(latents) > 1 else np.ones(components.shape[0])
        latent_variance = np.where(latent_variance < 1.0e-6, 1.0e-6, latent_variance)

        reconstructed = central_flat[None, :] + latents @ components
        reconstruction_rmse_mean = float(np.sqrt(np.mean(np.square(flat - reconstructed))))

        return cls(
            metadata=metadata,
            central_form=central_flat.reshape(metadata.frame_count, -1),
            components=components,
            latent_mean=latent_mean,
            latent_variance=latent_variance,
            feature_offset=feature_offset,
            feature_scale=feature_scale,
            reconstruction_rmse_mean=reconstruction_rmse_mean,
            demo_count=len(demonstrations),
        )

    def canonicalize(self, trajectory: np.ndarray) -> CanonicalMovement:
        return canonicalize_trajectory(
            trajectory,
            frame_count=self.metadata.frame_count,
            feature_names=self.metadata.feature_names,
        )

    def encode(self, trajectory: np.ndarray) -> SchemaCode:
        flat = self._normalized_flat(trajectory)
        centered = flat - self.central_form.reshape(-1)
        latent = centered @ self.components.T
        reconstructed = self.central_form.reshape(-1) + latent @ self.components
        residual_rmse = float(np.sqrt(np.mean(np.square(flat - reconstructed))))
        return SchemaCode(latent=latent, residual_rmse=residual_rmse)

    def decode(self, code: SchemaCode | np.ndarray) -> np.ndarray:
        latent = code.latent if isinstance(code, SchemaCode) else np.asarray(code, dtype=np.float64)
        flat = self.central_form.reshape(-1) + latent @ self.components
        normalized = flat.reshape(self.central_form.shape)
        return normalized * self.feature_scale + self.feature_offset

    def distance(self, other: "MovementSchemaV1 | np.ndarray") -> float:
        if isinstance(other, MovementSchemaV1):
            return float(np.sqrt(np.mean(np.square(self.central_form - other.central_form))))
        return self.score_demo(other).distance

    def score_demo(self, trajectory: np.ndarray) -> SchemaScore:
        code = self.encode(trajectory)
        latent_delta = code.latent - self.latent_mean
        latent_distance = float(np.sqrt(np.mean(np.square(latent_delta) / self.latent_variance)))
        reconstructed = self.decode(code)
        canonical = self.canonicalize(trajectory).values
        reconstruction_rmse = float(np.sqrt(np.mean(np.square(canonical - reconstructed))))
        endpoint_error = float(np.sqrt(np.mean(np.square(canonical[-1] - reconstructed[-1]))))
        distance = reconstruction_rmse + 0.25 * endpoint_error + 0.05 * latent_distance
        return SchemaScore(
            distance=distance,
            latent_distance=latent_distance,
            reconstruction_rmse=reconstruction_rmse,
            endpoint_error=endpoint_error,
            residual_rmse=code.residual_rmse,
        )

    def sample(self, n: int, seed: int) -> list[np.ndarray]:
        if n < 1:
            raise SchemaError("sample count must be positive")
        rng = np.random.default_rng(seed)
        latents = rng.normal(self.latent_mean, np.sqrt(self.latent_variance), size=(n, self.components.shape[0]))
        return [self.decode(latent) for latent in latents]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": {
                "action_label": self.metadata.action_label,
                "frame_count": self.metadata.frame_count,
                "component_count": self.metadata.component_count,
                "feature_names": list(self.metadata.feature_names),
                "canonicalization": self.metadata.canonicalization,
            },
            "demo_count": self.demo_count,
            "central_form": self.central_form.astype(float).tolist(),
            "components": self.components.astype(float).tolist(),
            "latent_mean": self.latent_mean.astype(float).tolist(),
            "latent_variance": self.latent_variance.astype(float).tolist(),
            "feature_offset": self.feature_offset.astype(float).tolist(),
            "feature_scale": self.feature_scale.astype(float).tolist(),
            "reconstruction_rmse_mean": float(self.reconstruction_rmse_mean),
            "factorization": {
                "invariant_motor_form": "central_form + action-conditioned PCA components",
                "goal_task_context": "feature fields preserve endpoint, gripper, joint, and action context",
                "embodiment_adapter": "canonicalization records frame count and feature ordering",
                "residual_channel": "schema residual is measured separately; .zpbot remains a support codec",
            },
            "scoring": {
                "distance": "reconstruction RMSE + 0.25 * endpoint error + 0.05 * latent covariance distance",
                "version": "schema_score_v1",
            },
        }

    @classmethod
    def from_packet(cls, packet: dict[str, Any]) -> "MovementSchemaV1":
        if packet.get("schema_version") != SCHEMA_VERSION:
            raise SchemaError("unsupported movement schema packet version")
        meta = packet["metadata"]
        metadata = SchemaMetadata(
            action_label=str(meta["action_label"]),
            frame_count=int(meta["frame_count"]),
            component_count=int(meta["component_count"]),
            feature_names=tuple(str(name) for name in meta.get("feature_names", [])),
            canonicalization=str(meta.get("canonicalization", "start_relative_resampled_v1")),
        )
        return cls(
            metadata=metadata,
            central_form=np.asarray(packet["central_form"], dtype=np.float64),
            components=np.asarray(packet["components"], dtype=np.float64),
            latent_mean=np.asarray(packet["latent_mean"], dtype=np.float64),
            latent_variance=np.asarray(packet["latent_variance"], dtype=np.float64),
            feature_offset=np.asarray(packet["feature_offset"], dtype=np.float64),
            feature_scale=np.asarray(packet["feature_scale"], dtype=np.float64),
            reconstruction_rmse_mean=float(packet["reconstruction_rmse_mean"]),
            demo_count=int(packet["demo_count"]),
        )

    def packet_size_bytes(self) -> int:
        return len(json.dumps(self.to_packet(), sort_keys=True, separators=(",", ":")).encode("utf-8"))

    def _normalized_flat(self, trajectory: np.ndarray) -> np.ndarray:
        canonical = self.canonicalize(trajectory).values
        normalized = (canonical - self.feature_offset) / self.feature_scale
        return normalized.reshape(-1)


def canonicalize_trajectory(
    trajectory: np.ndarray,
    frame_count: int = 128,
    feature_names: tuple[str, ...] = (),
) -> CanonicalMovement:
    arr = _validate_trajectory(trajectory)
    if frame_count < 8:
        raise SchemaError("frame_count must be at least 8")
    resampled = resample_trajectory(arr, frame_count)
    body_relative = resampled - resampled[0:1, :]
    velocity = np.gradient(body_relative, axis=0)
    values = np.concatenate([body_relative, velocity], axis=1)
    names = _canonical_feature_names(arr.shape[1], feature_names)
    return CanonicalMovement(values=values, feature_names=names, frame_count=frame_count)


def resample_trajectory(trajectory: np.ndarray, frame_count: int) -> np.ndarray:
    arr = _validate_trajectory(trajectory)
    old_x = np.linspace(0.0, 1.0, arr.shape[0])
    new_x = np.linspace(0.0, 1.0, frame_count)
    out = np.empty((frame_count, arr.shape[1]), dtype=np.float64)
    for idx in range(arr.shape[1]):
        out[:, idx] = np.interp(new_x, old_x, arr[:, idx])
    return out


def packet_to_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _fit_components(centered: np.ndarray, requested_count: int) -> np.ndarray:
    if requested_count < 1:
        raise SchemaError("component_count must be positive")
    max_components = max(1, min(requested_count, centered.shape[0] - 1, centered.shape[1]))
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    return vt[:max_components].astype(np.float64, copy=False)


def _validate_trajectory(trajectory: np.ndarray) -> np.ndarray:
    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise SchemaError("trajectory must be a 2D array [frames, features]")
    if arr.shape[0] < 8:
        raise SchemaError("trajectory must include at least 8 frames")
    if arr.shape[1] < 1:
        raise SchemaError("trajectory must include at least one feature")
    if not np.isfinite(arr).all():
        raise SchemaError("trajectory contains non-finite values")
    return arr


def _canonical_feature_names(width: int, feature_names: tuple[str, ...]) -> tuple[str, ...]:
    base_names = feature_names if len(feature_names) == width else tuple(f"feature_{idx}" for idx in range(width))
    relative = tuple(f"rel:{name}" for name in base_names)
    velocity = tuple(f"vel:{name}" for name in base_names)
    return relative + velocity
