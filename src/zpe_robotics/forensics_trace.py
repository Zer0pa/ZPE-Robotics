"""Movement-episode forensics pilot gate over ViFailback telemetry."""

from __future__ import annotations

import datetime as dt
import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .schema import canonicalize_trajectory
from .utils import sha256_file, write_json, write_text


DEFAULT_FORENSICS_SEED = 20260612
DEFAULT_FRAME_COUNT = 128
DEFAULT_WINDOW_FRACTION = 0.25
PRIMARY_METHOD = "incident_trace"
FULL_REVIEW_BASELINE = "full_episode"


@dataclass(frozen=True)
class EpisodeRecord:
    task: str
    episode: int
    role: str
    path: Path
    arrays: dict[str, np.ndarray]
    frame_count: int
    failure_detection: str
    failure_type: str | None = None
    failure_subtask: str | None = None
    avoid_frame: int | None = None
    correct_frame: int | None = None

    @property
    def episode_id(self) -> str:
        return f"{self.task}/episode_{self.episode}"


@dataclass(frozen=True)
class ReferenceModel:
    task: str
    frame_count: int
    center: np.ndarray
    scale: np.ndarray
    pca_mean: np.ndarray
    pca_components: np.ndarray
    feature_names: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceWindow:
    method: str
    start: int
    end: int
    center: int
    frame_count: int
    score_peak: float

    @property
    def fraction(self) -> float:
        return float((self.end - self.start + 1) / max(1, self.frame_count))

    def covers(self, frame: int | None) -> bool:
        return isinstance(frame, int) and self.start <= frame <= self.end

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "start": self.start,
            "end": self.end,
            "center": self.center,
            "frame_count": self.frame_count,
            "score_peak": self.score_peak,
            "window_fraction": self.fraction,
        }


def run_forensics_pilot_gate(
    dataset_root: Path,
    annotation_root: Path,
    selection_path: Path,
    output_dir: Path,
    seed: int = DEFAULT_FORENSICS_SEED,
    frame_count: int = DEFAULT_FRAME_COUNT,
    window_fraction: float = DEFAULT_WINDOW_FRACTION,
) -> dict[str, Any]:
    """Run the local Phase 12 pilot and emit proof artifacts."""

    dataset_root = dataset_root.resolve()
    annotation_root = annotation_root.resolve()
    selection_path = selection_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    episodes = load_selected_episodes(dataset_root, annotation_root, selection)
    references = {
        task: fit_reference_model(task, [ep for ep in task_eps if ep.role == "success_reference"], frame_count)
        for task, task_eps in episodes.items()
    }

    traces: list[dict[str, Any]] = []
    window_rows: list[dict[str, Any]] = []
    for task, task_eps in episodes.items():
        reference = references[task]
        for episode in task_eps:
            if episode.role != "failure_eval":
                continue
            method_scores = score_episode_methods(episode, reference)
            windows = {
                method: window_from_scores(method, scores, episode.frame_count, window_fraction)
                for method, scores in method_scores.items()
            }
            windows.update(fixed_windows(episode.frame_count, window_fraction))
            windows[FULL_REVIEW_BASELINE] = EvidenceWindow(
                method=FULL_REVIEW_BASELINE,
                start=0,
                end=max(0, episode.frame_count - 1),
                center=max(0, (episode.frame_count - 1) // 2),
                frame_count=episode.frame_count,
                score_peak=1.0,
            )
            trace = incident_trace_payload(episode, windows[PRIMARY_METHOD])
            traces.append(trace)
            for method, window in sorted(windows.items()):
                window_rows.append(evaluate_window(episode, window))

    evidence_eval = aggregate_evidence_windows(window_rows)
    baseline_comparison = compare_forensics_baselines(evidence_eval)
    verdict = final_forensics_pilot_verdict(baseline_comparison)

    write_json(output_dir / "ENVIRONMENT.json", environment_payload())
    write_json(output_dir / "SOURCE_HASHES.json", source_hashes(Path(__file__).resolve().parents[2]))
    write_json(output_dir / "PILOT_DATASET_MANIFEST.json", dataset_manifest(episodes, selection_path))
    write_json(output_dir / "incident_trace_schema.json", incident_trace_schema())
    write_json(output_dir / "phase_event_trace.json", traces)
    write_json(output_dir / "prediction_error_trace.json", prediction_error_summary(window_rows))
    write_json(output_dir / "incident_trace.json", traces)
    write_json(output_dir / "failure_localization_eval.json", failure_localization_eval(window_rows))
    write_json(output_dir / "evidence_window_eval.json", evidence_eval)
    write_json(output_dir / "baseline_comparison_forensics.json", baseline_comparison)
    write_json(output_dir / "FINAL_GATE_VERDICT.json", verdict)
    write_text(output_dir / "FALSIFICATION_MEMO.md", falsification_memo(verdict, baseline_comparison))
    write_text(output_dir / "forensics_pilot_report.md", pilot_report(verdict, baseline_comparison))
    write_text(output_dir / "COMMANDS.log", command_log(dataset_root, annotation_root, selection_path, output_dir))
    write_failure_cases(output_dir / "failure_cases", window_rows, baseline_comparison)
    return verdict


def load_selected_episodes(
    dataset_root: Path,
    annotation_root: Path,
    selection: dict[str, Any],
) -> dict[str, list[EpisodeRecord]]:
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("h5py is required for ViFailback HDF5 loading") from exc

    records: dict[str, list[EpisodeRecord]] = {}
    for task, task_selection in selection["tasks"].items():
        annotation_rows = load_annotation_rows(annotation_root / task / f"{task}_annotations.json")
        task_records: list[EpisodeRecord] = []
        selected = {
            "success_reference": task_selection["success_reference_episodes"],
            "failure_eval": sorted(
                ep for eps in task_selection["failure_eval_episodes_by_type"].values() for ep in eps
            ),
        }
        for role, episode_ids in selected.items():
            for episode in episode_ids:
                path = dataset_root / "raw_data" / task / f"episode_{episode}.hdf5"
                if not path.exists():
                    raise FileNotFoundError(path)
                row = annotation_rows.get(int(episode))
                if row is None:
                    raise ValueError(f"missing annotation row for {task} episode {episode}")
                with h5py.File(path, "r") as handle:
                    arrays = read_telemetry_arrays(handle)
                frame_total = min(array.shape[0] for array in arrays.values())
                arrays = {name: np.asarray(array[:frame_total], dtype=np.float64) for name, array in arrays.items()}
                avoid_frame, correct_frame = keyframe_targets(row)
                task_records.append(
                    EpisodeRecord(
                        task=task,
                        episode=int(episode),
                        role=role,
                        path=path,
                        arrays=arrays,
                        frame_count=frame_total,
                        failure_detection=str(row.get("failure_detection", "")),
                        failure_type=row.get("failure_type"),
                        failure_subtask=row.get("failure_subtask"),
                        avoid_frame=avoid_frame,
                        correct_frame=correct_frame,
                    )
                )
        records[task] = task_records
    return records


def load_annotation_rows(path: Path) -> dict[int, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {episode_from_video(row["video"]): row for row in rows}


def episode_from_video(video_path: str) -> int:
    marker = "episode_"
    if marker not in video_path:
        raise ValueError(f"cannot parse episode from {video_path!r}")
    suffix = video_path.split(marker, maxsplit=1)[1]
    return int(suffix.split("_", maxsplit=1)[0])


def keyframe_targets(row: dict[str, Any]) -> tuple[int | None, int | None]:
    avoid = None
    correct = None
    for item in row.get("keyframe", []) or []:
        avoid = avoid if avoid is not None else frame_from_keyframe_path(item.get("avoid_keyframe"))
        correct = correct if correct is not None else frame_from_keyframe_path(item.get("correct_keyframe"))
    return avoid, correct


def frame_from_keyframe_path(path: str | None) -> int | None:
    if not path:
        return None
    name = Path(path).name
    prefix = name.split("_", maxsplit=1)[0]
    return int(prefix) if prefix.isdigit() else None


def read_telemetry_arrays(handle: Any) -> dict[str, np.ndarray]:
    fields = {
        "action": "action",
        "action_eef": "action_eef",
        "qpos": "observations/qpos",
        "qvel": "observations/qvel",
        "effort": "observations/effort",
    }
    arrays = {}
    for name, hdf5_path in fields.items():
        if hdf5_path not in handle:
            raise ValueError(f"missing required HDF5 field: {hdf5_path}")
        arrays[name] = as_matrix(handle[hdf5_path][()])
    return arrays


def as_matrix(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 1:
        return array[:, None]
    if array.ndim > 2:
        return array.reshape(array.shape[0], -1)
    return array


def episode_matrix(episode: EpisodeRecord) -> tuple[np.ndarray, tuple[str, ...]]:
    parts = []
    names = []
    for field in ("action", "action_eef", "qpos", "qvel", "effort"):
        values = episode.arrays[field]
        parts.append(values)
        names.extend(f"{field}_{idx}" for idx in range(values.shape[1]))
    return np.concatenate(parts, axis=1), tuple(names)


def fit_reference_model(task: str, success_episodes: list[EpisodeRecord], frame_count: int) -> ReferenceModel:
    if len(success_episodes) < 2:
        raise ValueError("forensics reference model requires at least two success episodes")
    matrices = []
    feature_names: tuple[str, ...] | None = None
    for episode in success_episodes:
        matrix, names = episode_matrix(episode)
        feature_names = names
        matrices.append(canonicalize_trajectory(matrix, frame_count=frame_count, feature_names=names).values)
    stack = np.stack(matrices, axis=0)
    center = np.median(stack, axis=0)
    scale = np.std(stack, axis=(0, 1))
    scale = np.where(scale < 1.0e-6, 1.0, scale)
    normalized = ((stack - center) / scale).reshape(len(matrices), -1)
    pca_mean = np.mean(normalized, axis=0)
    centered = normalized - pca_mean
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    component_count = max(1, min(4, vt.shape[0]))
    return ReferenceModel(
        task=task,
        frame_count=frame_count,
        center=center,
        scale=scale,
        pca_mean=pca_mean,
        pca_components=vt[:component_count],
        feature_names=feature_names or (),
    )


def score_episode_methods(episode: EpisodeRecord, reference: ReferenceModel) -> dict[str, np.ndarray]:
    matrix, names = episode_matrix(episode)
    canonical = canonicalize_trajectory(matrix, frame_count=reference.frame_count, feature_names=names).values
    normalized = (canonical - reference.center) / reference.scale
    raw_residual = vector_norm(normalized)
    simple_event = event_score(normalized)
    pca_residual = pca_reconstruction_residual(normalized, reference)
    dct_residual = spectral_residual(normalized, kind="dct", keep=8)
    fft_residual = spectral_residual(normalized, kind="fft", keep=8)
    incident = incident_trace_score(raw_residual, simple_event, pca_residual, dct_residual, fft_residual)
    return {
        PRIMARY_METHOD: original_length_score(incident, episode.frame_count),
        "raw_residual": original_length_score(raw_residual, episode.frame_count),
        "pca_residual": original_length_score(pca_residual, episode.frame_count),
        "dct_residual": original_length_score(dct_residual, episode.frame_count),
        "fft_residual": original_length_score(fft_residual, episode.frame_count),
        "simple_event": original_length_score(simple_event, episode.frame_count),
    }


def vector_norm(values: np.ndarray) -> np.ndarray:
    return np.sqrt(np.mean(np.square(values), axis=1))


def event_score(values: np.ndarray) -> np.ndarray:
    velocity = np.vstack([np.zeros((1, values.shape[1])), np.diff(values, axis=0)])
    acceleration = np.vstack([np.zeros((1, values.shape[1])), np.diff(velocity, axis=0)])
    return robust_z(vector_norm(velocity)) + 0.5 * robust_z(vector_norm(acceleration))


def pca_reconstruction_residual(values: np.ndarray, reference: ReferenceModel) -> np.ndarray:
    flat = values.reshape(-1)
    centered = flat - reference.pca_mean
    latent = centered @ reference.pca_components.T
    reconstructed = reference.pca_mean + latent @ reference.pca_components
    residual = (flat - reconstructed).reshape(values.shape)
    return vector_norm(residual)


def spectral_residual(values: np.ndarray, kind: str, keep: int) -> np.ndarray:
    if kind == "fft":
        coeffs = np.fft.rfft(values, axis=0)
        coeffs[keep:, :] = 0.0
        smooth = np.fft.irfft(coeffs, n=values.shape[0], axis=0)
        return vector_norm(values - smooth)
    basis = dct_basis(values.shape[0], min(keep, values.shape[0]))
    coeffs = basis @ values
    smooth = basis.T @ coeffs
    return vector_norm(values - smooth)


def dct_basis(length: int, keep: int) -> np.ndarray:
    n = np.arange(length, dtype=np.float64)
    k = np.arange(keep, dtype=np.float64)[:, None]
    basis = np.cos(np.pi * (n + 0.5) * k / length)
    basis[0, :] *= np.sqrt(1.0 / length)
    if keep > 1:
        basis[1:, :] *= np.sqrt(2.0 / length)
    return basis


def incident_trace_score(
    raw_residual: np.ndarray,
    simple_event: np.ndarray,
    pca_residual: np.ndarray,
    dct_residual: np.ndarray,
    fft_residual: np.ndarray,
) -> np.ndarray:
    departure = np.maximum.accumulate(robust_z(raw_residual))
    consensus = np.mean(
        np.stack(
            [
                robust_z(raw_residual),
                robust_z(simple_event),
                robust_z(pca_residual),
                robust_z(dct_residual),
                robust_z(fft_residual),
            ],
            axis=0,
        ),
        axis=0,
    )
    return 0.55 * consensus + 0.30 * robust_z(simple_event) + 0.15 * departure


def robust_z(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    scale = 1.4826 * mad if mad > 1.0e-8 else float(np.std(values))
    if scale < 1.0e-8:
        return np.zeros_like(values, dtype=np.float64)
    return (values - median) / scale


def original_length_score(scores: np.ndarray, length: int) -> np.ndarray:
    if len(scores) == length:
        return np.asarray(scores, dtype=np.float64)
    x_old = np.linspace(0.0, 1.0, len(scores))
    x_new = np.linspace(0.0, 1.0, length)
    return np.interp(x_new, x_old, scores).astype(np.float64)


def window_from_scores(method: str, scores: np.ndarray, frame_count: int, fraction: float) -> EvidenceWindow:
    width = window_width(frame_count, fraction)
    center = int(np.argmax(scores)) if len(scores) else 0
    start = max(0, min(center - width // 2, frame_count - width))
    end = min(frame_count - 1, start + width - 1)
    return EvidenceWindow(
        method=method,
        start=int(start),
        end=int(end),
        center=int(center),
        frame_count=int(frame_count),
        score_peak=float(scores[center]) if len(scores) else 0.0,
    )


def fixed_windows(frame_count: int, fraction: float) -> dict[str, EvidenceWindow]:
    width = window_width(frame_count, fraction)
    starts = {
        "fixed_start_25pct": 0,
        "fixed_middle_25pct": max(0, (frame_count - width) // 2),
        "fixed_end_25pct": max(0, frame_count - width),
    }
    return {
        method: EvidenceWindow(
            method=method,
            start=start,
            end=min(frame_count - 1, start + width - 1),
            center=start + width // 2,
            frame_count=frame_count,
            score_peak=1.0,
        )
        for method, start in starts.items()
    }


def window_width(frame_count: int, fraction: float) -> int:
    if not 0.0 < fraction <= 1.0:
        raise ValueError("window fraction must be in (0, 1]")
    return max(1, int(np.floor(frame_count * fraction)))


def evaluate_window(episode: EpisodeRecord, window: EvidenceWindow) -> dict[str, Any]:
    targets = [episode.avoid_frame, episode.correct_frame]
    covered = [window.covers(frame) for frame in targets]
    target_errors = [abs(window.center - frame) for frame in targets if isinstance(frame, int)]
    return {
        "task": episode.task,
        "episode": episode.episode,
        "episode_id": episode.episode_id,
        "failure_type": episode.failure_type,
        "failure_subtask": episode.failure_subtask,
        "avoid_frame": episode.avoid_frame,
        "correct_frame": episode.correct_frame,
        "method": window.method,
        "window": window.to_dict(),
        "covered_keyframes": int(sum(covered)),
        "target_keyframes": int(len(targets)),
        "keyframe_coverage": float(sum(covered) / max(1, len(targets))),
        "both_keyframes_covered": bool(all(covered)),
        "min_abs_frame_error": int(min(target_errors)) if target_errors else None,
        "mean_abs_frame_error": float(np.mean(target_errors)) if target_errors else None,
    }


def aggregate_evidence_windows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["task"], row["method"]), []).append(row)
    task_methods: dict[str, dict[str, Any]] = {}
    for (task, method), method_rows in sorted(grouped.items()):
        task_methods.setdefault(task, {})[method] = aggregate_method_rows(method_rows)
    return {"schema_version": 1, "task_methods": task_methods, "rows": rows}


def aggregate_method_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    covered = sum(row["covered_keyframes"] for row in rows)
    total = sum(row["target_keyframes"] for row in rows)
    errors = [row["mean_abs_frame_error"] for row in rows if row["mean_abs_frame_error"] is not None]
    fractions = [row["window"]["window_fraction"] for row in rows]
    return {
        "episode_count": len(rows),
        "keyframe_coverage": float(covered / max(1, total)),
        "both_keyframes_episode_rate": float(np.mean([row["both_keyframes_covered"] for row in rows])),
        "median_window_fraction": float(np.median(fractions)) if fractions else 0.0,
        "median_mean_abs_frame_error": float(np.median(errors)) if errors else None,
        "mean_abs_frame_error": float(np.mean(errors)) if errors else None,
    }


def compare_forensics_baselines(evidence_eval: dict[str, Any]) -> dict[str, Any]:
    task_results = {}
    for task, methods in evidence_eval["task_methods"].items():
        primary = methods[PRIMARY_METHOD]
        candidates = {
            method: metrics
            for method, metrics in methods.items()
            if method not in {PRIMARY_METHOD, FULL_REVIEW_BASELINE}
        }
        best_name, best_metrics = best_non_full_baseline(candidates)
        primary_beats = beats_method(primary, best_metrics)
        task_results[task] = {
            "primary_method": PRIMARY_METHOD,
            "primary": primary,
            "best_non_full_baseline_method": best_name,
            "best_non_full_baseline": best_metrics,
            "primary_beats_best_non_full_baseline": primary_beats,
            "full_review": methods[FULL_REVIEW_BASELINE],
            "pilot_acceptance": {
                "coverage_at_least_0_80": primary["keyframe_coverage"] >= 0.80,
                "window_fraction_at_most_0_25": primary["median_window_fraction"] <= 0.25 + 1.0e-9,
                "beats_best_non_full_baseline": primary_beats,
            },
        }
    return {
        "schema_version": 1,
        "primary_method": PRIMARY_METHOD,
        "task_results": task_results,
        "success_criteria": {
            "both_tasks_coverage_at_least_0_80": all(
                row["pilot_acceptance"]["coverage_at_least_0_80"] for row in task_results.values()
            ),
            "both_tasks_window_fraction_at_most_0_25": all(
                row["pilot_acceptance"]["window_fraction_at_most_0_25"] for row in task_results.values()
            ),
            "beats_best_non_full_baseline_on_both_tasks": all(
                row["pilot_acceptance"]["beats_best_non_full_baseline"] for row in task_results.values()
            ),
        },
    }


def best_non_full_baseline(candidates: dict[str, dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    def key(item: tuple[str, dict[str, Any]]) -> tuple[float, float]:
        _, metrics = item
        error = metrics["median_mean_abs_frame_error"]
        return (metrics["keyframe_coverage"], -float(error if error is not None else 1.0e9))

    return max(candidates.items(), key=key)


def beats_method(primary: dict[str, Any], baseline: dict[str, Any]) -> bool:
    coverage_delta = primary["keyframe_coverage"] - baseline["keyframe_coverage"]
    if coverage_delta > 1.0e-9:
        return True
    if abs(coverage_delta) > 1.0e-9:
        return False
    primary_error = primary["median_mean_abs_frame_error"]
    baseline_error = baseline["median_mean_abs_frame_error"]
    if primary_error is None or baseline_error is None:
        return False
    return float(primary_error) < 0.8 * float(baseline_error)


def final_forensics_pilot_verdict(comparison: dict[str, Any]) -> dict[str, Any]:
    criteria = comparison["success_criteria"]
    continue_full_gate = all(criteria.values())
    baseline_wins = not criteria["beats_best_non_full_baseline_on_both_tasks"]
    status = "pilot_continue_to_full_gate" if continue_full_gate else "pilot_abandon_forensics_trace"
    return {
        "schema_version": 1,
        "date": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "terminal_verdict": status,
        "product_worthy": False,
        "readme_claim_upgrade_allowed": False,
        "pilot_continue_to_full_gate": continue_full_gate,
        "baseline_wins_or_ties": baseline_wins,
        "success_criteria": criteria,
        "claim_boundary": {
            "full_phase12_product_gate_unrun": True,
            "pilot_can_only_justify_full_gate_spend_or_storage": True,
        },
    }


def incident_trace_payload(episode: EpisodeRecord, window: EvidenceWindow) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "episode_id": episode.episode_id,
        "task": episode.task,
        "episode": episode.episode,
        "failure_type_hypothesis": "telemetry_anomaly_window",
        "failure_type_label": episode.failure_type,
        "failure_subtask_label": episode.failure_subtask,
        "evidence_window": window.to_dict(),
        "targets": {
            "avoid_frame": episode.avoid_frame,
            "correct_frame": episode.correct_frame,
            "avoid_covered": window.covers(episode.avoid_frame),
            "correct_covered": window.covers(episode.correct_frame),
        },
        "raw_evidence_channels": sorted(episode.arrays),
        "missing_fields": [
            "force_torque",
            "tactile",
            "contact_state",
            "controller_residual",
        ],
        "claim_boundary": "pilot telemetry evidence only; no contact/controller diagnosis",
    }


def incident_trace_schema() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "fields": [
            "episode_id",
            "task",
            "episode",
            "failure_type_hypothesis",
            "failure_type_label",
            "failure_subtask_label",
            "evidence_window",
            "targets",
            "raw_evidence_channels",
            "missing_fields",
            "claim_boundary",
        ],
        "forbidden_inputs": [
            "failure_detection",
            "failure_type",
            "failure_subtask",
            "avoid_keyframe",
            "correct_keyframe",
            "correction_text",
        ],
    }


def prediction_error_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "window_rows": rows,
        "note": "Scores are summarized as evidence windows; labels are evaluation targets only.",
    }


def failure_localization_eval(rows: list[dict[str, Any]]) -> dict[str, Any]:
    primary_rows = [row for row in rows if row["method"] == PRIMARY_METHOD]
    return {
        "schema_version": 1,
        "method": PRIMARY_METHOD,
        "episode_count": len(primary_rows),
        "failure_type_macro_f1": None,
        "failure_subtask_macro_f1": None,
        "reason": "Pilot evaluates evidence-window timing/compression only; failure type/subtask labels are not used as model inputs.",
        "primary_window_rows": primary_rows,
    }


def dataset_manifest(episodes: dict[str, list[EpisodeRecord]], selection_path: Path) -> dict[str, Any]:
    files = []
    for task_eps in episodes.values():
        for episode in task_eps:
            files.append(
                {
                    "task": episode.task,
                    "episode": episode.episode,
                    "role": episode.role,
                    "path": str(episode.path),
                    "size_bytes": episode.path.stat().st_size,
                    "sha256": sha256_file(episode.path),
                    "frame_count": episode.frame_count,
                }
            )
    return {
        "schema_version": 1,
        "selection_path": str(selection_path),
        "file_count": len(files),
        "files": sorted(files, key=lambda row: (row["task"], row["episode"])),
    }


def environment_payload() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "created_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def source_hashes(repo_root: Path) -> dict[str, str]:
    source = repo_root / "src" / "zpe_robotics" / "forensics_trace.py"
    return {str(source.relative_to(repo_root)): sha256_file(source)}


def command_log(dataset_root: Path, annotation_root: Path, selection_path: Path, output_dir: Path) -> str:
    return (
        "python -m zpe_robotics.forensics_trace "
        f"--dataset-root {dataset_root} --annotation-root {annotation_root} "
        f"--selection {selection_path} --output-dir {output_dir}\n"
    )


def falsification_memo(verdict: dict[str, Any], comparison: dict[str, Any]) -> str:
    lines = [
        "# Forensics Pilot Falsification Memo",
        "",
        f"Terminal verdict: `{verdict['terminal_verdict']}`",
        "",
        "This is a pilot-only gate. It cannot produce a product pass or README upgrade.",
        "",
        "## Task Results",
        "",
    ]
    for task, result in comparison["task_results"].items():
        lines.extend(
            [
                f"### {task}",
                "",
                f"- primary coverage: `{result['primary']['keyframe_coverage']:.4f}`",
                f"- primary median window fraction: `{result['primary']['median_window_fraction']:.4f}`",
                f"- best non-full baseline: `{result['best_non_full_baseline_method']}`",
                f"- baseline coverage: `{result['best_non_full_baseline']['keyframe_coverage']:.4f}`",
                f"- primary beats baseline: `{result['primary_beats_best_non_full_baseline']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "- Contact/force/tactile/slip/controller-residual claims remain blocked.",
            "- Failure type/subtask diagnosis remains unevaluated in this pilot.",
            "- Full two-task Phase 12 product gate remains unrun.",
        ]
    )
    return "\n".join(lines) + "\n"


def pilot_report(verdict: dict[str, Any], comparison: dict[str, Any]) -> str:
    return falsification_memo(verdict, comparison)


def write_failure_cases(output_dir: Path, rows: list[dict[str, Any]], comparison: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    primary_rows = [row for row in rows if row["method"] == PRIMARY_METHOD and row["keyframe_coverage"] < 1.0]
    write_json(output_dir / "primary_missed_keyframes.json", primary_rows)
    losses = [
        {"task": task, **result}
        for task, result in comparison["task_results"].items()
        if not result["primary_beats_best_non_full_baseline"]
    ]
    write_json(output_dir / "baseline_losses.json", losses)
