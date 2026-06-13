"""Functional movement curation gate over real RoboMimic quality/outcome data."""

from __future__ import annotations

import datetime as dt
import json
import math
import platform
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .schema import canonicalize_trajectory
from .schema_baselines import dct_lowpass_vector, fft_lowpass_vector
from .utils import sha256_file, stable_json_dumps, write_json, write_text


DEFAULT_FUNCTIONAL_SEED = 20260616
QUALITY_TASKS = ("can", "lift", "square")
OUTCOME_TASKS = ("can", "lift")
QUALITY_LABELS = ("worse", "better")
QUALITY_LABEL_RANK = {"worse": 0, "okay": 1, "better": 2}
OUTCOME_LABEL_RANK = {"failure": 0, "success": 1}
PRIMARY_METHOD = "functional_phase_event"


@dataclass(frozen=True)
class FunctionalDemo:
    demo_id: str
    task: str
    family: str
    episode_id: str
    source_path: str
    split: str
    label_kind: str
    label: str
    label_rank: int
    reward_sum: float
    final_reward: float
    reward_onset: int | None
    arrays: dict[str, np.ndarray]

    @property
    def frame_count(self) -> int:
        return int(self.arrays["actions"].shape[0])


@dataclass(frozen=True)
class FunctionalDataset:
    demos: list[FunctionalDemo]
    manifest: dict[str, Any]


def run_functional_curation_gate(
    dataset_root: Path,
    output_dir: Path,
    seed: int = DEFAULT_FUNCTIONAL_SEED,
    frame_count: int = 32,
    budget_per_class: int = 5,
) -> dict[str, Any]:
    """Run the Phase 09 functional curation experiment and emit all artifacts."""

    dataset_root = dataset_root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    command = (
        "python -m zpe_robotics.schema_eval run-functional-curation-gate "
        f"--dataset-root {dataset_root} --output-dir {output_dir}"
    )
    write_text(output_dir / "COMMANDS.log", command + "\n")
    write_json(output_dir / "ENVIRONMENT.json", _environment_payload())
    write_json(output_dir / "SOURCE_HASHES.json", _source_hashes(Path(__file__).resolve().parents[2]))

    dataset = load_functional_dataset(dataset_root, seed=seed)
    write_json(output_dir / "FUNCTIONAL_DATASET_MANIFEST.json", dataset.manifest)

    features = build_feature_bank(dataset.demos, frame_count=frame_count, seed=seed)
    feature_surface = feature_surface_payload(features)
    write_json(output_dir / "functional_feature_surface.json", feature_surface)

    phase_graph = functional_phase_graph(dataset.demos, features)
    quality_eval = evaluate_functional_quality(dataset.demos, features, seed=seed)
    outliers = detect_functional_outliers(dataset.demos, features, seed=seed)
    representatives = select_functional_representatives(
        dataset.demos,
        features,
        budget_per_class=budget_per_class,
        seed=seed,
    )
    diversity = select_functional_diversity(dataset.demos, features, budget_per_class=budget_per_class, seed=seed)
    phase_eval = evaluate_phase_segmentation(dataset.demos, features)
    baseline_comparison = compare_functional_baselines(
        quality_eval,
        outliers,
        representatives,
        diversity,
        feature_surface,
    )
    verdict = final_functional_verdict(baseline_comparison)

    write_json(output_dir / "functional_phase_graph.json", phase_graph)
    write_json(output_dir / "phase_segmentation_eval.json", phase_eval)
    write_json(output_dir / "functional_quality_eval.json", quality_eval)
    write_json(output_dir / "functional_representatives.json", representatives)
    write_json(output_dir / "functional_outliers.json", outliers)
    write_json(output_dir / "functional_diversity_selection.json", diversity)
    write_json(output_dir / "baseline_comparison_functional.json", baseline_comparison)
    write_json(output_dir / "FINAL_GATE_VERDICT.json", verdict)
    _write_failure_cases(output_dir / "failure_cases", quality_eval, outliers, baseline_comparison)
    write_text(output_dir / "FALSIFICATION_MEMO.md", falsification_memo(verdict, baseline_comparison))
    write_text(output_dir / "functional_curation_report.md", functional_report(verdict, baseline_comparison))
    if verdict["status"] in {"abandon_functional_curation", "prior_art_dominates_abandon"}:
        write_text(output_dir / "ABANDON_FUNCTIONAL_CURATION_WEDGE.md", abandon_decision_text(verdict, baseline_comparison))
    return verdict


def load_functional_dataset(dataset_root: Path, seed: int = DEFAULT_FUNCTIONAL_SEED) -> FunctionalDataset:
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("h5py is required for RoboMimic HDF5 loading") from exc

    demos: list[FunctionalDemo] = []
    files = []
    for task in QUALITY_TASKS:
        path = dataset_root / "v1.5" / task / "mh" / "low_dim_v15.hdf5"
        if not path.exists():
            raise FileNotFoundError(f"missing MH quality dataset: {path}")
        with h5py.File(path, "r") as handle:
            quality_map = _mh_quality_map(handle)
            split_map = _mh_split_map(handle)
            for episode_id in sorted(quality_map, key=_demo_index):
                label = quality_map[episode_id]
                if label not in QUALITY_LABELS:
                    continue
                group = handle["data"][episode_id]
                arrays = _read_demo_arrays(group)
                rewards = arrays["rewards"]
                demos.append(
                    FunctionalDemo(
                        demo_id=f"mh/{task}/{episode_id}",
                        task=task,
                        family="mh",
                        episode_id=episode_id,
                        source_path=str(path),
                        split=split_map.get(episode_id, "train"),
                        label_kind="quality",
                        label=label,
                        label_rank=QUALITY_LABEL_RANK[label],
                        reward_sum=float(np.sum(rewards)),
                        final_reward=float(rewards[-1]),
                        reward_onset=_reward_onset(rewards),
                        arrays=arrays,
                    )
                )
        files.append(_file_manifest(path, task=task, family="mh"))

    for task in OUTCOME_TASKS:
        path = dataset_root / "v1.5" / task / "mg" / "low_dim_sparse_v15.hdf5"
        if not path.exists():
            raise FileNotFoundError(f"missing MG outcome dataset: {path}")
        with h5py.File(path, "r") as handle:
            for episode_id in sorted(handle["data"].keys(), key=_demo_index):
                group = handle["data"][episode_id]
                arrays = _read_demo_arrays(group)
                rewards = arrays["rewards"]
                label = "success" if float(rewards[-1]) > 0.0 else "failure"
                demos.append(
                    FunctionalDemo(
                        demo_id=f"mg/{task}/{episode_id}",
                        task=task,
                        family="mg",
                        episode_id=episode_id,
                        source_path=str(path),
                        split=_mg_split(episode_id),
                        label_kind="outcome",
                        label=label,
                        label_rank=OUTCOME_LABEL_RANK[label],
                        reward_sum=float(np.sum(rewards)),
                        final_reward=float(rewards[-1]),
                        reward_onset=_reward_onset(rewards),
                        arrays=arrays,
                    )
                )
        files.append(_file_manifest(path, task=task, family="mg"))

    paired_path = dataset_root / "v1.5" / "can" / "paired" / "low_dim_v15.hdf5"
    if paired_path.exists():
        with h5py.File(paired_path, "r") as handle:
            split_map = _paired_split_map(handle)
            for episode_id in sorted(handle["data"].keys(), key=_demo_index):
                group = handle["data"][episode_id]
                arrays = _read_demo_arrays(group)
                rewards = arrays["rewards"]
                label = "success" if float(rewards[-1]) > 0.0 else "failure"
                demos.append(
                    FunctionalDemo(
                        demo_id=f"paired/can/{episode_id}",
                        task="can",
                        family="paired",
                        episode_id=episode_id,
                        source_path=str(paired_path),
                        split=split_map.get(episode_id, "train"),
                        label_kind="paired_diagnostic",
                        label=label,
                        label_rank=OUTCOME_LABEL_RANK[label],
                        reward_sum=float(np.sum(rewards)),
                        final_reward=float(rewards[-1]),
                        reward_onset=_reward_onset(rewards),
                        arrays=arrays,
                    )
                )
        files.append(_file_manifest(paired_path, task="can", family="paired"))

    manifest = {
        "schema_version": 1,
        "dataset_root": str(dataset_root),
        "source": "robomimic/robomimic_datasets",
        "seed": seed,
        "files": files,
        "demo_count": len(demos),
        "counts": _dataset_counts(demos),
        "split_policy": {
            "mh": "Use official worse_train/worse_valid and better_train/better_valid mask keys; okay is excluded from primary binary quality tests.",
            "mg": "Use deterministic episode_id modulo 10 validation split frozen before feature extraction.",
            "paired": "Use official train/valid masks when present; diagnostic only and excluded from product-pass count.",
        },
        "label_policy": {
            "mh": "worse versus better operator-proficiency masks as real mixed-quality proxy labels",
            "mg": "final sparse reward as success/failure outcome label",
            "paired": "final reward good/bad sanity check only",
        },
        "reward_leakage_policy": "Reward values and reward onset are used for labels and audit only, not as classifier input features.",
        "readme_claim_upgrade_allowed": False,
    }
    return FunctionalDataset(demos=demos, manifest=manifest)


def build_feature_bank(
    demos: list[FunctionalDemo],
    frame_count: int = 32,
    seed: int = DEFAULT_FUNCTIONAL_SEED,
) -> dict[str, Any]:
    rows = []
    raw_vectors = []
    dct_vectors = []
    fft_vectors = []
    event_vectors = []
    deminf_vectors = []
    s2i_vectors = []
    functional_vectors = []
    for demo in demos:
        sequence = _trajectory_matrix(demo)
        raw = canonicalize_trajectory(sequence, frame_count=frame_count).values.reshape(-1)
        event = _event_features(demo)
        deminf = _deminf_proxy_features(demo)
        s2i = _s2i_proxy_features(demo)
        functional = _functional_phase_features(demo, event, deminf, s2i)
        rows.append(_feature_row(demo, event, functional))
        raw_vectors.append(raw)
        dct_vectors.append(dct_lowpass_vector(sequence, frame_count=frame_count, keep_coeffs=8))
        fft_vectors.append(fft_lowpass_vector(sequence, frame_count=frame_count, keep_coeffs=8))
        event_vectors.append(event)
        deminf_vectors.append(deminf)
        s2i_vectors.append(s2i)
        functional_vectors.append(functional)

    method_matrices = {
        "raw_phase_aligned": np.stack(raw_vectors, axis=0),
        "dct_lowpass": np.stack(dct_vectors, axis=0),
        "fft_lowpass": np.stack(fft_vectors, axis=0),
        "event_heuristic": np.stack(event_vectors, axis=0),
        "deminf_proxy": np.stack(deminf_vectors, axis=0),
        "s2i_keyframe_proxy": np.stack(s2i_vectors, axis=0),
        PRIMARY_METHOD: np.stack(functional_vectors, axis=0),
    }
    method_matrices["raw_medoid_centrality"] = method_matrices["raw_phase_aligned"]
    method_matrices["raw_nearest_demo"] = method_matrices["raw_phase_aligned"]
    return {
        "schema_version": 1,
        "frame_count": frame_count,
        "seed": seed,
        "demo_ids": [demo.demo_id for demo in demos],
        "rows": rows,
        "methods": method_matrices,
        "method_descriptions": {
            PRIMARY_METHOD: "event, phase, correction, object/eef, gripper, S2I-like, and DemInf-like non-reward features",
            "raw_phase_aligned": "start-relative resampled action/eef/gripper/object trajectory plus velocity",
            "raw_nearest_demo": "1-nearest demonstration classifier on the raw phase-aligned vector",
            "raw_medoid_centrality": "nearest class medoid on the raw phase-aligned vector",
            "dct_lowpass": "low-pass DCT coefficients over action/eef/gripper/object sequence",
            "fft_lowpass": "low-pass FFT coefficients over action/eef/gripper/object sequence",
            "pca_global": "target-local PCA projection fitted only on the active target train split",
            "event_heuristic": "simple gripper/eef event timing and magnitude heuristics",
            "deminf_proxy": "local action-divergence and transition-diversity proxy features",
            "s2i_keyframe_proxy": "gripper-change and velocity-keyframe segment proxy features",
        },
    }


def feature_surface_payload(features: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "frame_count": features["frame_count"],
        "reward_leakage_policy": "No reward-derived values are included in classifier vectors.",
        "methods": {},
    }
    for name, matrix in features["methods"].items():
        payload["methods"][name] = {
            "description": features["method_descriptions"][name],
            "shape": list(matrix.shape),
            "zlib_bytes": _zlib_matrix_bytes(matrix),
        }
    payload["methods"]["pca_global"] = {
        "description": features["method_descriptions"]["pca_global"],
        "shape": "target_local",
        "zlib_bytes": None,
    }
    return payload


def evaluate_functional_quality(
    demos: list[FunctionalDemo],
    features: dict[str, Any],
    seed: int = DEFAULT_FUNCTIONAL_SEED,
) -> dict[str, Any]:
    targets = _evaluation_targets(demos)
    target_results = {}
    for target in targets:
        target_results[target["target_id"]] = _evaluate_target(target, features, seed=seed)
    primary_targets = {
        key: result
        for key, result in target_results.items()
        if not result["target"].get("diagnostic_only", False)
    }
    return {
        "schema_version": 1,
        "metric": "balanced_accuracy and macro_f1 on frozen validation splits",
        "primary_method": PRIMARY_METHOD,
        "targets": target_results,
        "primary_target_count": len(primary_targets),
        "primary_target_ids": sorted(primary_targets),
    }


def detect_functional_outliers(
    demos: list[FunctionalDemo],
    features: dict[str, Any],
    seed: int = DEFAULT_FUNCTIONAL_SEED,
) -> dict[str, Any]:
    targets = _evaluation_targets(demos)
    results = {}
    for target in targets:
        if target.get("diagnostic_only", False):
            continue
        positive_label = target["positive_label"]
        bad_label = _bad_label_for_target(target)
        train_ids = [demo_id for demo_id in target["train_ids"] if _demo_by_id(demos, demo_id).label == positive_label]
        valid_ids = list(target["valid_ids"])
        labels = np.asarray([1 if _demo_by_id(demos, demo_id).label == bad_label else 0 for demo_id in valid_ids])
        if len(set(labels.tolist())) < 2 or not train_ids:
            continue
        method_rows = {}
        for method, matrix in features["methods"].items():
            scores = _good_centroid_outlier_scores(features, method, train_ids, valid_ids)
            method_rows[method] = _outlier_metric(scores, labels, valid_ids)
        pca_scores = _pca_good_centroid_outlier_scores(features, train_ids, valid_ids)
        method_rows["pca_global"] = _outlier_metric(pca_scores, labels, valid_ids)
        raw_scores = _knn_distance_scores(features, "raw_phase_aligned", train_ids, valid_ids, neighbors=7)
        method_rows["lof_like_knn_density"] = _outlier_metric(raw_scores, labels, valid_ids)
        iso_scores = _isolation_projection_scores(features, "raw_phase_aligned", train_ids, valid_ids, seed=seed)
        method_rows["isolation_projection"] = _outlier_metric(iso_scores, labels, valid_ids)
        primary_ap = method_rows[PRIMARY_METHOD]["average_precision"]
        baseline_names = [name for name in method_rows if name != PRIMARY_METHOD]
        best_baseline = max(baseline_names, key=lambda name: method_rows[name]["average_precision"])
        results[target["target_id"]] = {
            "target": target,
            "bad_label": bad_label,
            "good_training_label": positive_label,
            "methods": method_rows,
            "primary_average_precision": primary_ap,
            "best_baseline_method": best_baseline,
            "best_baseline_average_precision": method_rows[best_baseline]["average_precision"],
            "pass_vs_baselines": primary_ap >= method_rows[best_baseline]["average_precision"] + 0.01,
        }
    return {
        "schema_version": 1,
        "label_policy": "worse quality and failure outcomes are treated as natural outlier classes; no synthetic corruption is used",
        "targets": results,
    }


def select_functional_representatives(
    demos: list[FunctionalDemo],
    features: dict[str, Any],
    budget_per_class: int = 5,
    seed: int = DEFAULT_FUNCTIONAL_SEED,
) -> dict[str, Any]:
    targets = _evaluation_targets(demos)
    results = {}
    for target in targets:
        if target.get("diagnostic_only", False):
            continue
        methods = {}
        for method in (PRIMARY_METHOD, "raw_phase_aligned", "dct_lowpass", "fft_lowpass"):
            selected = _select_medoid_then_farthest(features, method, target["train_ids"], budget_per_class)
            methods[method] = _representative_eval(features, method, selected, target["valid_ids"])
        pca_selected = _select_medoid_then_farthest_pca(features, target["train_ids"], budget_per_class)
        methods["pca_global"] = _representative_eval_pca(features, pca_selected, target["train_ids"], target["valid_ids"])
        random_selected = _select_random(target["train_ids"], budget_per_class, seed + len(target["target_id"]))
        methods["random"] = _representative_eval(features, PRIMARY_METHOD, random_selected, target["valid_ids"])
        best_baseline = min(
            [name for name in methods if name != PRIMARY_METHOD],
            key=lambda name: methods[name]["mean_nearest_distance"],
        )
        results[target["target_id"]] = {
            "target": target,
            "budget_per_class": budget_per_class,
            "methods": methods,
            "best_baseline_method": best_baseline,
            "primary_mean_nearest_distance": methods[PRIMARY_METHOD]["mean_nearest_distance"],
            "best_baseline_mean_nearest_distance": methods[best_baseline]["mean_nearest_distance"],
            "pass_vs_baselines": methods[PRIMARY_METHOD]["mean_nearest_distance"]
            <= methods[best_baseline]["mean_nearest_distance"] * 0.99,
        }
    return {"schema_version": 1, "targets": results}


def select_functional_diversity(
    demos: list[FunctionalDemo],
    features: dict[str, Any],
    budget_per_class: int = 5,
    seed: int = DEFAULT_FUNCTIONAL_SEED,
) -> dict[str, Any]:
    targets = _evaluation_targets(demos)
    results = {}
    for target in targets:
        if target.get("diagnostic_only", False):
            continue
        positive_train = [demo_id for demo_id in target["train_ids"] if _demo_by_id(demos, demo_id).label == target["positive_label"]]
        positive_valid = [demo_id for demo_id in target["valid_ids"] if _demo_by_id(demos, demo_id).label == target["positive_label"]]
        if not positive_train or not positive_valid:
            continue
        methods = {}
        for method in (PRIMARY_METHOD, "raw_phase_aligned", "dct_lowpass", "fft_lowpass"):
            selected = _select_farthest_first(features, method, positive_train, budget_per_class)
            methods[method] = _diversity_eval(features, method, selected, positive_valid)
        pca_selected = _select_farthest_first_pca(features, positive_train, budget_per_class)
        methods["pca_global"] = _diversity_eval_pca(features, pca_selected, positive_train, positive_valid)
        random_selected = _select_random(positive_train, budget_per_class, seed)
        methods["random"] = _diversity_eval(features, PRIMARY_METHOD, random_selected, positive_valid)
        best_baseline = min(
            [name for name in methods if name != PRIMARY_METHOD],
            key=lambda name: methods[name]["mean_coverage_distance"],
        )
        results[target["target_id"]] = {
            "target": target,
            "budget_per_class": budget_per_class,
            "methods": methods,
            "best_baseline_method": best_baseline,
            "pass_vs_baselines": methods[PRIMARY_METHOD]["mean_coverage_distance"]
            <= methods[best_baseline]["mean_coverage_distance"] * 0.99,
        }
    return {"schema_version": 1, "targets": results}


def functional_phase_graph(demos: list[FunctionalDemo], features: dict[str, Any]) -> dict[str, Any]:
    by_group: dict[str, list[dict[str, Any]]] = {}
    rows_by_id = {row["demo_id"]: row for row in features["rows"]}
    for demo in demos:
        key = f"{demo.family}/{demo.task}/{demo.label}"
        row = rows_by_id[demo.demo_id]
        by_group.setdefault(key, []).append(
            {
                "demo_id": demo.demo_id,
                "frame_count": demo.frame_count,
                "first_close_ratio": row["audit_events"]["first_close_ratio"],
                "min_eef_object_distance_ratio": row["audit_events"]["min_eef_object_distance_ratio"],
                "late_correction_ratio": row["audit_events"]["late_correction_ratio"],
                "reward_onset_ratio": None
                if demo.reward_onset is None
                else float(demo.reward_onset / max(1, demo.frame_count - 1)),
                "final_reward": demo.final_reward,
            }
        )
    summaries = {}
    for key, rows in by_group.items():
        summaries[key] = {
            "count": len(rows),
            "first_close_ratio_mean": _mean(row["first_close_ratio"] for row in rows),
            "min_eef_object_distance_ratio_mean": _mean(row["min_eef_object_distance_ratio"] for row in rows),
            "late_correction_ratio_mean": _mean(row["late_correction_ratio"] for row in rows),
            "reward_onset_ratio_mean": _mean(
                row["reward_onset_ratio"] for row in rows if row["reward_onset_ratio"] is not None
            ),
        }
    return {
        "schema_version": 1,
        "phase_model": "proxy phase graph: approach -> gripper event -> object/eef proximity -> late correction -> reward/outcome audit",
        "contact_policy": "No force/tactile fields are present; contact is inferred only from gripper and eef-object proxy events.",
        "reward_policy": "Reward onset is reported for audit, not used as classifier input.",
        "summaries": summaries,
        "examples": {key: rows[:5] for key, rows in by_group.items()},
    }


def evaluate_phase_segmentation(demos: list[FunctionalDemo], features: dict[str, Any]) -> dict[str, Any]:
    rows = features["rows"]
    eval_rows = []
    for group_key in sorted({(demo.family, demo.task, demo.label) for demo in demos}):
        family, task, label = group_key
        group_rows = [row for row in rows if row["family"] == family and row["task"] == task and row["label"] == label]
        if not group_rows:
            continue
        close = [row["audit_events"]["first_close_ratio"] for row in group_rows]
        proximity = [row["audit_events"]["min_eef_object_distance_ratio"] for row in group_rows]
        correction = [row["audit_events"]["late_correction_ratio"] for row in group_rows]
        eval_rows.append(
            {
                "group": f"{family}/{task}/{label}",
                "count": len(group_rows),
                "first_close_ratio_iqr": _iqr(close),
                "min_eef_object_distance_ratio_iqr": _iqr(proximity),
                "late_correction_ratio_iqr": _iqr(correction),
            }
        )
    return {
        "schema_version": 1,
        "status": "proxy_only_no_human_phase_labels",
        "metric": "within-label event timing interquartile ranges; lower means a more stable functional channel",
        "cannot_count_as_product_pass": True,
        "rows": eval_rows,
    }


def compare_functional_baselines(
    quality_eval: dict[str, Any],
    outliers: dict[str, Any],
    representatives: dict[str, Any],
    diversity: dict[str, Any],
    feature_surface: dict[str, Any],
) -> dict[str, Any]:
    target_rows = {}
    material_margin = 0.01
    complement_margin = 0.005
    primary_bytes = feature_surface["methods"][PRIMARY_METHOD]["zlib_bytes"]
    raw_bytes = feature_surface["methods"]["raw_phase_aligned"]["zlib_bytes"]
    compact_enough = primary_bytes <= 0.35 * raw_bytes
    for target_id, payload in quality_eval["targets"].items():
        target = payload["target"]
        if target.get("diagnostic_only", False):
            continue
        primary = payload["methods"][PRIMARY_METHOD]
        best_baseline_name = payload["best_baseline_method"]
        best = payload["methods"][best_baseline_name]
        margin = primary["balanced_accuracy"] - best["balanced_accuracy"]
        target_rows[target_id] = {
            "target": target,
            "primary_balanced_accuracy": primary["balanced_accuracy"],
            "primary_macro_f1": primary["macro_f1"],
            "best_baseline_method": best_baseline_name,
            "best_baseline_balanced_accuracy": best["balanced_accuracy"],
            "balanced_accuracy_margin": margin,
            "beats_baselines": margin >= material_margin,
            "materially_complements": margin >= -complement_margin and compact_enough,
            "compact_feature_ratio_vs_raw": primary_bytes / max(1, raw_bytes),
        }
    beating_targets = [key for key, row in target_rows.items() if row["beats_baselines"]]
    complement_targets = [key for key, row in target_rows.items() if row["materially_complements"]]
    outlier_passes = [key for key, row in outliers["targets"].items() if row["pass_vs_baselines"]]
    representative_passes = [key for key, row in representatives["targets"].items() if row["pass_vs_baselines"]]
    diversity_passes = [key for key, row in diversity["targets"].items() if row["pass_vs_baselines"]]
    return {
        "schema_version": 1,
        "primary_method": PRIMARY_METHOD,
        "material_margin": material_margin,
        "complement_margin": complement_margin,
        "target_results": target_rows,
        "beating_target_ids": beating_targets,
        "complement_target_ids": complement_targets,
        "outlier_pass_target_ids": outlier_passes,
        "representative_pass_target_ids": representative_passes,
        "diversity_pass_target_ids": diversity_passes,
        "primary_method_storage": feature_surface["methods"][PRIMARY_METHOD],
        "raw_method_storage": feature_surface["methods"]["raw_phase_aligned"],
        "success_criteria": {
            "beats_or_complements_two_real_functional_targets": len(set(beating_targets + complement_targets)) >= 2,
            "better_outlier_detection_than_baselines": len(outlier_passes) >= 2,
            "better_representative_selection_than_baselines": len(representative_passes) >= 2,
            "better_functional_diversity_than_baselines": len(diversity_passes) >= 2,
            "audit_only": False,
        },
    }


def final_functional_verdict(comparison: dict[str, Any]) -> dict[str, Any]:
    criteria = comparison["success_criteria"]
    two_target_edge = bool(criteria["beats_or_complements_two_real_functional_targets"])
    support_edges = sum(
        [
            bool(criteria["better_outlier_detection_than_baselines"]),
            bool(criteria["better_representative_selection_than_baselines"]),
            bool(criteria["better_functional_diversity_than_baselines"]),
        ]
    )
    if two_target_edge and support_edges >= 1:
        status = "functional_curation_primitive_pass"
        product_worthy = True
        reason = "Functional features beat or materially complement baselines on at least two real functional targets and one supporting curation task."
    elif two_target_edge:
        status = "audit_only_no_algorithmic_edge"
        product_worthy = False
        reason = "Classification complement exists, but supporting curation tasks did not clear baselines; keep audit only."
    else:
        baseline_winners = [
            row["best_baseline_method"]
            for row in comparison["target_results"].values()
            if row["best_baseline_method"] in {"deminf_proxy", "s2i_keyframe_proxy"}
        ]
        if len(baseline_winners) >= 2:
            status = "prior_art_dominates_abandon"
            reason = "Prior-art-style proxy baselines explain the measured signal better than the functional composite."
        else:
            status = "abandon_functional_curation"
            reason = "Functional features did not clear the two-real-target baseline gate."
        product_worthy = False
    return {
        "schema_version": 1,
        "status": status,
        "product_worthy": product_worthy,
        "scope": "function-aware robot demonstration dataset curation",
        "broad_movement_memory_claim_allowed": False,
        "nature_claim_allowed": False,
        "readme_claim_upgrade_allowed": False,
        "paired_can_counted_for_product_pass": False,
        "success_criteria": criteria,
        "reason": reason,
    }


def falsification_memo(verdict: dict[str, Any], comparison: dict[str, Any]) -> str:
    lines = [
        "# Falsification Memo",
        "",
        f"Final verdict: `{verdict['status']}`.",
        "",
        "This gate tested whether a function-aware feature set built from gripper timing, eef/object relations, correction signatures, and local data-quality proxies could beat required baselines on real RoboMimic MH/MG data.",
        "",
        "Reward values were withheld from classifier input to avoid outcome leakage. Paired Can was diagnostic only.",
        "",
        "## Target Results",
        "",
    ]
    for target_id, row in sorted(comparison["target_results"].items()):
        lines.append(
            "- "
            f"{target_id}: primary balanced accuracy {row['primary_balanced_accuracy']:.4f}; "
            f"best baseline `{row['best_baseline_method']}` {row['best_baseline_balanced_accuracy']:.4f}; "
            f"margin {row['balanced_accuracy_margin']:.4f}."
        )
    lines.extend(
        [
            "",
            "## Falsifiers",
            "",
            "- Product pass is rejected if wins are only audit, only Paired Can, or only trajectory shape.",
            "- Product pass is rejected if raw, DCT/FFT/PCA, event-only, DemInf-style, or S2I-style baselines explain the signal.",
            "- Nature framing remains a design trigger only; no nature claim is allowed from this gate.",
        ]
    )
    return "\n".join(lines) + "\n"


def functional_report(verdict: dict[str, Any], comparison: dict[str, Any]) -> str:
    lines = [
        "# Functional Curation Report",
        "",
        f"Verdict: `{verdict['status']}`.",
        "",
        "The tested mechanism used function-oriented features rather than trajectory-shape retrieval: phase/event timing, object/eef relations, gripper events, correction signatures, and local action-divergence/transition-diversity proxies.",
        "",
        "## Baseline Result",
        "",
    ]
    for target_id, row in sorted(comparison["target_results"].items()):
        outcome = "pass" if row["beats_baselines"] else "fail"
        lines.append(
            f"- {target_id}: {outcome}; primary={row['primary_balanced_accuracy']:.4f}, "
            f"best_baseline={row['best_baseline_method']}:{row['best_baseline_balanced_accuracy']:.4f}."
        )
    return "\n".join(lines) + "\n"


def abandon_decision_text(verdict: dict[str, Any], comparison: dict[str, Any]) -> str:
    lines = [
        "# Abandon Functional Curation Wedge",
        "",
        f"Verdict: `{verdict['status']}`.",
        "",
        "The functional feature composite did not beat or materially complement required baselines on two real functional targets, and it did not clear the supporting outlier, representative, or diversity gates.",
        "",
        "## Why",
        "",
    ]
    for target_id, row in sorted(comparison["target_results"].items()):
        lines.append(
            f"- {target_id}: primary {row['primary_balanced_accuracy']:.4f}, "
            f"best baseline `{row['best_baseline_method']}` {row['best_baseline_balanced_accuracy']:.4f}."
        )
    lines.extend(
        [
            "",
            "## Frozen Boundaries",
            "",
            "- Do not upgrade README or public claims.",
            "- Do not repackage this as broad movement memory.",
            "- Do not claim nature supports the method; no measurable primitive survived the falsifier.",
            "- Paired Can remains diagnostic and did not count toward product pass.",
            "",
            "## Next Honest Direction",
            "",
            "A future phase would need genuinely richer functional labels such as contact/force/tactile, intervention/recovery, human quality ratings, or downstream policy-training effects. Re-running more trajectory or phase-shape variants on this pivot is not justified by this gate.",
        ]
    )
    return "\n".join(lines) + "\n"


def _read_demo_arrays(group: Any) -> dict[str, np.ndarray]:
    actions = np.asarray(group["actions"], dtype=np.float64)
    if actions.ndim == 1:
        actions = actions[:, None]
    actions = actions[:, : min(actions.shape[1], 7)]
    obs = group["obs"]
    arrays = {
        "actions": actions,
        "eef": np.asarray(obs["robot0_eef_pos"], dtype=np.float64),
        "gripper": np.asarray(obs["robot0_gripper_qpos"], dtype=np.float64),
        "gripper_vel": np.asarray(obs["robot0_gripper_qvel"], dtype=np.float64),
        "object": np.asarray(obs["object"], dtype=np.float64),
        "rewards": np.asarray(group["rewards"], dtype=np.float64),
        "dones": np.asarray(group["dones"], dtype=np.float64) if "dones" in group else np.zeros(actions.shape[0]),
    }
    length = actions.shape[0]
    for name, values in arrays.items():
        if name in {"rewards", "dones"}:
            continue
        if values.shape[0] != length:
            raise ValueError(f"field {name} length mismatch")
    return arrays


def _trajectory_matrix(demo: FunctionalDemo) -> np.ndarray:
    arrays = demo.arrays
    object_values = _pad_width(arrays["object"], 14)
    return np.concatenate(
        [
            arrays["actions"],
            arrays["eef"],
            arrays["gripper"],
            arrays["gripper_vel"],
            object_values,
        ],
        axis=1,
    )


def _event_features(demo: FunctionalDemo) -> np.ndarray:
    arrays = demo.arrays
    eef = arrays["eef"]
    grip = arrays["gripper"]
    grip_vel = arrays["gripper_vel"]
    obj = arrays["object"]
    length = demo.frame_count
    grip_width = np.mean(grip, axis=1)
    grip_speed = np.linalg.norm(grip_vel, axis=1)
    eef_velocity = np.gradient(eef, axis=0)
    eef_speed = np.linalg.norm(eef_velocity, axis=1)
    object_pos = obj[:, :3] if obj.shape[1] >= 3 else np.zeros_like(eef)
    eef_obj = np.linalg.norm(eef - object_pos, axis=1)
    close_threshold = float(np.quantile(grip_width, 0.35))
    closed = grip_width <= close_threshold
    first_close = _first_true(closed)
    open_threshold = float(np.quantile(grip_width, 0.65))
    opened = grip_width >= open_threshold
    first_reopen = _first_true(opened & (np.arange(length) > max(first_close or 0, 0)))
    min_dist_idx = int(np.argmin(eef_obj))
    max_speed_idx = int(np.argmax(eef_speed))
    transitions = int(np.sum(np.abs(np.diff(closed.astype(int)))))
    return np.asarray(
        [
            length / 150.0,
            _ratio(first_close, length),
            _ratio(first_reopen, length),
            _ratio(min_dist_idx, length),
            _ratio(max_speed_idx, length),
            float(np.mean(grip_width)),
            float(np.std(grip_width)),
            float(np.min(grip_width)),
            float(np.max(grip_width)),
            float(np.mean(closed)),
            float(transitions),
            float(np.mean(grip_speed)),
            float(np.max(grip_speed)),
            float(np.mean(eef_speed)),
            float(np.max(eef_speed)),
            float(np.min(eef_obj)),
            float(np.mean(eef_obj)),
            float(eef_obj[-1]),
        ],
        dtype=np.float64,
    )


def _deminf_proxy_features(demo: FunctionalDemo) -> np.ndarray:
    arrays = demo.arrays
    actions = arrays["actions"]
    state = np.concatenate([arrays["eef"], arrays["object"], arrays["gripper"]], axis=1)
    action_delta = np.diff(actions, axis=0)
    transition = np.diff(state, axis=0)
    action_cov = _diag_log_variance(actions)
    transition_cov = _diag_log_variance(transition)
    return np.asarray(
        [
            float(np.mean(np.linalg.norm(actions, axis=1))),
            float(np.std(np.linalg.norm(actions, axis=1))),
            float(np.max(np.linalg.norm(actions, axis=1))),
            float(np.mean(np.linalg.norm(action_delta, axis=1))) if len(action_delta) else 0.0,
            float(np.std(np.linalg.norm(action_delta, axis=1))) if len(action_delta) else 0.0,
            float(np.mean(np.linalg.norm(transition, axis=1))) if len(transition) else 0.0,
            float(np.std(np.linalg.norm(transition, axis=1))) if len(transition) else 0.0,
            action_cov,
            transition_cov,
            _sign_change_rate(actions),
            _sign_change_rate(transition) if len(transition) else 0.0,
        ],
        dtype=np.float64,
    )


def _s2i_proxy_features(demo: FunctionalDemo) -> np.ndarray:
    arrays = demo.arrays
    eef = arrays["eef"]
    obj = arrays["object"]
    grip = arrays["gripper"]
    velocity = np.gradient(eef, axis=0)
    speed = np.linalg.norm(velocity, axis=1)
    grip_width = np.mean(grip, axis=1)
    key_indices = sorted(
        {
            0,
            len(speed) - 1,
            int(np.argmin(grip_width)),
            int(np.argmax(np.abs(np.gradient(grip_width)))),
            int(np.argmax(speed)),
            int(np.argmin(np.abs(speed - np.quantile(speed, 0.25)))),
        }
    )
    object_pos = obj[:, :3] if obj.shape[1] >= 3 else np.zeros_like(eef)
    vectors = []
    for idx in key_indices:
        vectors.extend(eef[idx].tolist())
        vectors.extend(object_pos[idx].tolist())
        vectors.append(float(grip_width[idx]))
        vectors.append(float(idx / max(1, len(speed) - 1)))
    while len(vectors) < 48:
        vectors.append(0.0)
    return np.asarray(vectors[:48], dtype=np.float64)


def _functional_phase_features(
    demo: FunctionalDemo,
    event: np.ndarray,
    deminf: np.ndarray,
    s2i: np.ndarray,
) -> np.ndarray:
    arrays = demo.arrays
    eef = arrays["eef"]
    obj = arrays["object"]
    actions = arrays["actions"]
    velocity = np.gradient(eef, axis=0)
    acceleration = np.gradient(velocity, axis=0)
    jerk = np.gradient(acceleration, axis=0)
    speed = np.linalg.norm(velocity, axis=1)
    object_pos = obj[:, :3] if obj.shape[1] >= 3 else np.zeros_like(eef)
    object_velocity = np.gradient(object_pos, axis=0)
    path = _path_length(eef)
    displacement = float(np.linalg.norm(eef[-1] - eef[0]))
    straightness = displacement / max(path, 1.0e-12)
    late_slice = slice(max(0, int(0.67 * demo.frame_count)), demo.frame_count)
    correction_features = np.asarray(
        [
            path,
            displacement,
            straightness,
            _path_length(object_pos),
            float(np.linalg.norm(object_pos[-1] - object_pos[0])),
            float(np.mean(np.linalg.norm(object_velocity, axis=1))),
            float(np.mean(np.linalg.norm(jerk, axis=1))),
            float(np.max(np.linalg.norm(jerk, axis=1))),
            float(np.mean(speed[late_slice]) / max(float(np.mean(speed)), 1.0e-12)),
            float(np.mean(np.linalg.norm(actions[late_slice], axis=1)) / max(float(np.mean(np.linalg.norm(actions, axis=1))), 1.0e-12)),
            _turning_rate(velocity),
            _speed_minima_count(speed) / max(1, demo.frame_count),
        ],
        dtype=np.float64,
    )
    endpoint = np.concatenate(
        [
            eef[0],
            eef[-1],
            object_pos[0],
            object_pos[-1],
            np.mean(obj, axis=0)[: min(6, obj.shape[1])],
            np.std(obj, axis=0)[: min(6, obj.shape[1])],
        ]
    )
    return np.concatenate([event, deminf, s2i, correction_features, endpoint]).astype(np.float64)


def _feature_row(demo: FunctionalDemo, event: np.ndarray, functional: np.ndarray) -> dict[str, Any]:
    return {
        "demo_id": demo.demo_id,
        "family": demo.family,
        "task": demo.task,
        "episode_id": demo.episode_id,
        "split": demo.split,
        "label_kind": demo.label_kind,
        "label": demo.label,
        "label_rank": demo.label_rank,
        "frame_count": demo.frame_count,
        "reward_sum": demo.reward_sum,
        "final_reward": demo.final_reward,
        "reward_onset": demo.reward_onset,
        "audit_events": {
            "first_close_ratio": float(event[1]),
            "first_reopen_ratio": float(event[2]),
            "min_eef_object_distance_ratio": float(event[3]),
            "max_speed_ratio": float(event[4]),
            "closed_fraction": float(event[9]),
            "gripper_transitions": float(event[10]),
            "late_correction_ratio": float(functional[18 + 11]) if functional.shape[0] > 29 else 0.0,
        },
    }


def _evaluation_targets(demos: list[FunctionalDemo]) -> list[dict[str, Any]]:
    targets = []
    for task in QUALITY_TASKS:
        task_demos = [demo for demo in demos if demo.family == "mh" and demo.task == task and demo.label in QUALITY_LABELS]
        if task_demos:
            targets.append(_target_payload(f"mh_{task}_quality_worse_vs_better", task_demos, "better", diagnostic=False))
    for task in OUTCOME_TASKS:
        task_demos = [demo for demo in demos if demo.family == "mg" and demo.task == task]
        if task_demos:
            targets.append(_target_payload(f"mg_{task}_outcome_success_vs_failure", task_demos, "success", diagnostic=False))
    paired = [demo for demo in demos if demo.family == "paired" and demo.task == "can"]
    if paired:
        targets.append(_target_payload("paired_can_diagnostic_good_vs_bad", paired, "success", diagnostic=True))
    return targets


def _target_payload(
    target_id: str,
    demos: list[FunctionalDemo],
    positive_label: str,
    diagnostic: bool,
) -> dict[str, Any]:
    train_ids = [demo.demo_id for demo in demos if demo.split == "train"]
    valid_ids = [demo.demo_id for demo in demos if demo.split == "valid"]
    labels = sorted({demo.label for demo in demos})
    return {
        "target_id": target_id,
        "family": demos[0].family,
        "task": demos[0].task,
        "label_kind": demos[0].label_kind,
        "labels": labels,
        "positive_label": positive_label,
        "train_ids": train_ids,
        "valid_ids": valid_ids,
        "train_count": len(train_ids),
        "valid_count": len(valid_ids),
        "diagnostic_only": diagnostic,
    }


def _evaluate_target(target: dict[str, Any], features: dict[str, Any], seed: int) -> dict[str, Any]:
    train_idx = _indices_for_ids(features, target["train_ids"])
    valid_idx = _indices_for_ids(features, target["valid_ids"])
    labels = _labels_for_ids(features, target["train_ids"] + target["valid_ids"])
    train_labels = labels[: len(train_idx)]
    valid_labels = labels[len(train_idx) :]
    methods = {}
    for method, matrix in features["methods"].items():
        if method == "raw_nearest_demo":
            pred, scores = _nearest_demo_predict(matrix[train_idx], train_labels, matrix[valid_idx], valid_labels)
        elif method == "raw_medoid_centrality":
            pred, scores = _medoid_predict(matrix[train_idx], train_labels, matrix[valid_idx], valid_labels)
        else:
            pred, scores = _nearest_centroid_predict(matrix[train_idx], train_labels, matrix[valid_idx], valid_labels)
        methods[method] = _classification_metric(
            valid_labels,
            pred,
            scores,
            positive_label=target["positive_label"],
            valid_ids=target["valid_ids"],
        )
    raw = features["methods"]["raw_phase_aligned"]
    pca_train, pca_valid = _fit_pca_transform(raw[train_idx], raw[valid_idx], component_count=24)
    pca_pred, pca_scores = _nearest_centroid_predict(pca_train, train_labels, pca_valid, valid_labels)
    methods["pca_global"] = _classification_metric(
        valid_labels,
        pca_pred,
        pca_scores,
        positive_label=target["positive_label"],
        valid_ids=target["valid_ids"],
    )
    random_pred = _random_predictions(train_labels, len(valid_labels), seed + len(target["target_id"]))
    methods["random_prior"] = _classification_metric(
        valid_labels,
        random_pred,
        np.zeros((len(valid_labels), len(set(train_labels))), dtype=np.float64),
        positive_label=target["positive_label"],
        valid_ids=target["valid_ids"],
    )
    baseline_names = [name for name in methods if name != PRIMARY_METHOD]
    best_baseline = max(baseline_names, key=lambda name: methods[name]["balanced_accuracy"])
    return {
        "target": {key: value for key, value in target.items() if not key.endswith("_ids")},
        "methods": methods,
        "best_baseline_method": best_baseline,
        "primary_balanced_accuracy": methods[PRIMARY_METHOD]["balanced_accuracy"],
        "best_baseline_balanced_accuracy": methods[best_baseline]["balanced_accuracy"],
        "primary_minus_best_baseline": methods[PRIMARY_METHOD]["balanced_accuracy"]
        - methods[best_baseline]["balanced_accuracy"],
    }


def _nearest_centroid_predict(
    train: np.ndarray,
    train_labels: list[str],
    valid: np.ndarray,
    valid_labels: list[str],
) -> tuple[list[str], np.ndarray]:
    train, valid = _standardize(train, valid)
    labels = sorted(set(train_labels))
    centroids = np.stack([np.mean(train[[idx for idx, label in enumerate(train_labels) if label == name]], axis=0) for name in labels])
    distances = _distance_matrix(valid, centroids)
    pred = [labels[int(idx)] for idx in np.argmin(distances, axis=1)]
    return pred, -distances


def _medoid_predict(
    train: np.ndarray,
    train_labels: list[str],
    valid: np.ndarray,
    valid_labels: list[str],
) -> tuple[list[str], np.ndarray]:
    train, valid = _standardize(train, valid)
    labels = sorted(set(train_labels))
    medoids = []
    for label in labels:
        rows = train[[idx for idx, row_label in enumerate(train_labels) if row_label == label]]
        medoids.append(rows[int(np.argmin(np.sum(_distance_matrix(rows, rows), axis=1)))])
    medoid_matrix = np.stack(medoids, axis=0)
    distances = _distance_matrix(valid, medoid_matrix)
    pred = [labels[int(idx)] for idx in np.argmin(distances, axis=1)]
    return pred, -distances


def _nearest_demo_predict(
    train: np.ndarray,
    train_labels: list[str],
    valid: np.ndarray,
    valid_labels: list[str],
) -> tuple[list[str], np.ndarray]:
    train, valid = _standardize(train, valid)
    labels = sorted(set(train_labels))
    distances = _distance_matrix(valid, train)
    nearest = np.argmin(distances, axis=1)
    pred = [train_labels[int(idx)] for idx in nearest]
    label_scores = np.zeros((valid.shape[0], len(labels)), dtype=np.float64)
    for label_idx, label in enumerate(labels):
        label_train = [idx for idx, row_label in enumerate(train_labels) if row_label == label]
        label_scores[:, label_idx] = -np.min(distances[:, label_train], axis=1)
    return pred, label_scores


def _classification_metric(
    truth: list[str],
    pred: list[str],
    scores: np.ndarray,
    positive_label: str,
    valid_ids: list[str],
) -> dict[str, Any]:
    labels = sorted(set(truth) | set(pred))
    recalls = []
    f1s = []
    for label in labels:
        tp = sum(1 for t, p in zip(truth, pred, strict=True) if t == label and p == label)
        fn = sum(1 for t, p in zip(truth, pred, strict=True) if t == label and p != label)
        fp = sum(1 for t, p in zip(truth, pred, strict=True) if t != label and p == label)
        recall = tp / max(1, tp + fn)
        precision = tp / max(1, tp + fp)
        f1 = 0.0 if precision + recall == 0.0 else 2.0 * precision * recall / (precision + recall)
        recalls.append(recall)
        f1s.append(f1)
    positive_scores = _positive_scores(scores, labels, positive_label)
    truth_binary = [1 if label == positive_label else 0 for label in truth]
    failures = [
        {"demo_id": demo_id, "true_label": t, "predicted_label": p}
        for demo_id, t, p in zip(valid_ids, truth, pred, strict=True)
        if t != p
    ][:30]
    return {
        "count": len(truth),
        "accuracy": sum(1 for t, p in zip(truth, pred, strict=True) if t == p) / max(1, len(truth)),
        "balanced_accuracy": float(np.mean(recalls)) if recalls else 0.0,
        "macro_f1": float(np.mean(f1s)) if f1s else 0.0,
        "average_precision_positive": _average_precision(positive_scores, truth_binary),
        "labels": labels,
        "failure_count": sum(1 for t, p in zip(truth, pred, strict=True) if t != p),
        "sample_failures": failures,
    }


def _positive_scores(scores: np.ndarray, labels: list[str], positive_label: str) -> np.ndarray:
    if scores.size == 0 or positive_label not in labels:
        return np.zeros(scores.shape[0], dtype=np.float64)
    return scores[:, labels.index(positive_label)]


def _average_precision(scores: Iterable[float], labels: Iterable[int]) -> float:
    pairs = sorted(zip(scores, labels, strict=True), key=lambda item: float(item[0]), reverse=True)
    positives = sum(int(label) for _, label in pairs)
    if positives == 0:
        return 0.0
    hits = 0
    precision_sum = 0.0
    for rank, (_, label) in enumerate(pairs, start=1):
        if int(label):
            hits += 1
            precision_sum += hits / rank
    return float(precision_sum / positives)


def _outlier_metric(scores: np.ndarray, labels: np.ndarray, valid_ids: list[str]) -> dict[str, Any]:
    ap = _average_precision(scores, labels)
    cutoff = max(1, int(np.sum(labels)))
    order = np.argsort(-scores, kind="stable")
    top = order[:cutoff]
    hits = int(np.sum(labels[top]))
    return {
        "average_precision": ap,
        "precision_at_positive_count": hits / cutoff,
        "positive_count": int(np.sum(labels)),
        "top_review_hits": hits,
        "top_review_count": cutoff,
        "top_review_demo_ids": [valid_ids[int(idx)] for idx in top[:20]],
    }


def _good_centroid_outlier_scores(
    features: dict[str, Any],
    method: str,
    train_ids: list[str],
    valid_ids: list[str],
) -> np.ndarray:
    matrix = features["methods"][method]
    train_idx = _indices_for_ids(features, train_ids)
    valid_idx = _indices_for_ids(features, valid_ids)
    train, valid = _standardize(matrix[train_idx], matrix[valid_idx])
    centroid = np.mean(train, axis=0)
    return np.sqrt(np.mean(np.square(valid - centroid[None, :]), axis=1))


def _knn_distance_scores(
    features: dict[str, Any],
    method: str,
    train_ids: list[str],
    valid_ids: list[str],
    neighbors: int,
) -> np.ndarray:
    matrix = features["methods"][method]
    train_idx = _indices_for_ids(features, train_ids)
    valid_idx = _indices_for_ids(features, valid_ids)
    train, valid = _standardize(matrix[train_idx], matrix[valid_idx])
    distances = _distance_matrix(valid, train)
    k = min(neighbors, train.shape[0])
    return np.mean(np.sort(distances, axis=1)[:, :k], axis=1)


def _isolation_projection_scores(
    features: dict[str, Any],
    method: str,
    train_ids: list[str],
    valid_ids: list[str],
    seed: int,
    projection_count: int = 32,
) -> np.ndarray:
    matrix = features["methods"][method]
    train_idx = _indices_for_ids(features, train_ids)
    valid_idx = _indices_for_ids(features, valid_ids)
    train, valid = _standardize(matrix[train_idx], matrix[valid_idx])
    rng = np.random.default_rng(seed)
    projections = rng.normal(0.0, 1.0, size=(train.shape[1], min(projection_count, train.shape[1])))
    train_proj = train @ projections
    valid_proj = valid @ projections
    center = np.median(train_proj, axis=0)
    scale = np.median(np.abs(train_proj - center[None, :]), axis=0)
    scale = np.where(scale < 1.0e-8, 1.0, scale)
    return np.mean(np.abs(valid_proj - center[None, :]) / scale[None, :], axis=1)


def _pca_good_centroid_outlier_scores(
    features: dict[str, Any],
    train_ids: list[str],
    valid_ids: list[str],
) -> np.ndarray:
    matrix = features["methods"]["raw_phase_aligned"]
    train_idx = _indices_for_ids(features, train_ids)
    valid_idx = _indices_for_ids(features, valid_ids)
    train, valid = _fit_pca_transform(matrix[train_idx], matrix[valid_idx], component_count=24)
    train, valid = _standardize(train, valid)
    centroid = np.mean(train, axis=0)
    return np.sqrt(np.mean(np.square(valid - centroid[None, :]), axis=1))


def _representative_eval(
    features: dict[str, Any],
    method: str,
    selected_ids: list[str],
    valid_ids: list[str],
) -> dict[str, Any]:
    matrix = features["methods"][method]
    selected_idx = _indices_for_ids(features, selected_ids)
    valid_idx = _indices_for_ids(features, valid_ids)
    selected, valid = _standardize(matrix[selected_idx], matrix[valid_idx])
    distances = _distance_matrix(valid, selected)
    nearest = np.min(distances, axis=1)
    return {
        "selected_demo_ids": selected_ids,
        "selected_count": len(selected_ids),
        "mean_nearest_distance": float(np.mean(nearest)),
        "p95_nearest_distance": float(np.percentile(nearest, 95.0)),
    }


def _representative_eval_pca(
    features: dict[str, Any],
    selected_ids: list[str],
    fit_ids: list[str],
    valid_ids: list[str],
) -> dict[str, Any]:
    matrix = features["methods"]["raw_phase_aligned"]
    fit_idx = _indices_for_ids(features, fit_ids)
    selected_idx = _indices_for_ids(features, selected_ids)
    valid_idx = _indices_for_ids(features, valid_ids)
    fit_values, selected_and_valid = _fit_pca_transform(
        matrix[fit_idx],
        np.concatenate([matrix[selected_idx], matrix[valid_idx]], axis=0),
        component_count=24,
    )
    selected = selected_and_valid[: len(selected_idx)]
    valid = selected_and_valid[len(selected_idx) :]
    mean = np.mean(fit_values, axis=0)
    scale = np.std(fit_values, axis=0)
    scale = np.where(scale < 1.0e-8, 1.0, scale)
    selected = (selected - mean) / scale
    valid = (valid - mean) / scale
    distances = _distance_matrix(valid, selected)
    nearest = np.min(distances, axis=1)
    return {
        "selected_demo_ids": selected_ids,
        "selected_count": len(selected_ids),
        "mean_nearest_distance": float(np.mean(nearest)),
        "p95_nearest_distance": float(np.percentile(nearest, 95.0)),
    }


def _diversity_eval(
    features: dict[str, Any],
    method: str,
    selected_ids: list[str],
    valid_ids: list[str],
) -> dict[str, Any]:
    result = _representative_eval(features, method, selected_ids, valid_ids)
    result["mean_coverage_distance"] = result.pop("mean_nearest_distance")
    result["p95_coverage_distance"] = result.pop("p95_nearest_distance")
    return result


def _diversity_eval_pca(
    features: dict[str, Any],
    selected_ids: list[str],
    fit_ids: list[str],
    valid_ids: list[str],
) -> dict[str, Any]:
    result = _representative_eval_pca(features, selected_ids, fit_ids, valid_ids)
    result["mean_coverage_distance"] = result.pop("mean_nearest_distance")
    result["p95_coverage_distance"] = result.pop("p95_nearest_distance")
    return result


def _select_medoid_then_farthest(
    features: dict[str, Any],
    method: str,
    ids: list[str],
    budget: int,
) -> list[str]:
    if not ids:
        return []
    matrix = features["methods"][method][_indices_for_ids(features, ids)]
    matrix, _ = _standardize(matrix, matrix)
    distances = _distance_matrix(matrix, matrix)
    selected = [int(np.argmin(np.sum(distances, axis=1)))]
    while len(selected) < min(budget, len(ids)):
        nearest = np.min(distances[:, selected], axis=1)
        nearest[selected] = -1.0
        selected.append(int(np.argmax(nearest)))
    return [ids[idx] for idx in selected]


def _select_medoid_then_farthest_pca(features: dict[str, Any], ids: list[str], budget: int) -> list[str]:
    if not ids:
        return []
    matrix = features["methods"]["raw_phase_aligned"][_indices_for_ids(features, ids)]
    train, _ = _fit_pca_transform(matrix, matrix, component_count=24)
    distances = _distance_matrix(train, train)
    selected = [int(np.argmin(np.sum(distances, axis=1)))]
    while len(selected) < min(budget, len(ids)):
        nearest = np.min(distances[:, selected], axis=1)
        nearest[selected] = -1.0
        selected.append(int(np.argmax(nearest)))
    return [ids[idx] for idx in selected]


def _select_farthest_first(features: dict[str, Any], method: str, ids: list[str], budget: int) -> list[str]:
    if not ids:
        return []
    matrix = features["methods"][method][_indices_for_ids(features, ids)]
    matrix, _ = _standardize(matrix, matrix)
    centroid = np.mean(matrix, axis=0)
    distances_to_center = np.sqrt(np.mean(np.square(matrix - centroid[None, :]), axis=1))
    selected = [int(np.argmin(distances_to_center))]
    distances = _distance_matrix(matrix, matrix)
    while len(selected) < min(budget, len(ids)):
        nearest = np.min(distances[:, selected], axis=1)
        nearest[selected] = -1.0
        selected.append(int(np.argmax(nearest)))
    return [ids[idx] for idx in selected]


def _select_farthest_first_pca(features: dict[str, Any], ids: list[str], budget: int) -> list[str]:
    if not ids:
        return []
    matrix = features["methods"]["raw_phase_aligned"][_indices_for_ids(features, ids)]
    train, _ = _fit_pca_transform(matrix, matrix, component_count=24)
    centroid = np.mean(train, axis=0)
    distances_to_center = np.sqrt(np.mean(np.square(train - centroid[None, :]), axis=1))
    selected = [int(np.argmin(distances_to_center))]
    distances = _distance_matrix(train, train)
    while len(selected) < min(budget, len(ids)):
        nearest = np.min(distances[:, selected], axis=1)
        nearest[selected] = -1.0
        selected.append(int(np.argmax(nearest)))
    return [ids[idx] for idx in selected]


def _select_random(ids: list[str], budget: int, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    if not ids:
        return []
    indices = rng.permutation(len(ids))[: min(budget, len(ids))]
    return [ids[int(idx)] for idx in indices]


def _fit_pca_transform(
    train: np.ndarray,
    valid: np.ndarray,
    component_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(train, axis=0)
    centered_train = train - mean
    centered_valid = valid - mean
    keep = max(1, min(component_count, centered_train.shape[0], centered_train.shape[1]))
    covariance = centered_train.T @ centered_train / max(1, centered_train.shape[0] - 1)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1][:keep]
    components = vectors[:, order].T
    return centered_train @ components.T, centered_valid @ components.T


def _standardize(train: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(train, axis=0)
    scale = np.std(train, axis=0)
    scale = np.where(scale < 1.0e-8, 1.0, scale)
    return (train - mean) / scale, (valid - mean) / scale


def _distance_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left_sq = np.sum(np.square(left), axis=1, keepdims=True)
    right_sq = np.sum(np.square(right), axis=1, keepdims=True).T
    squared = np.maximum(left_sq + right_sq - 2.0 * (left @ right.T), 0.0)
    return np.sqrt(squared / max(1, left.shape[1]))


def _indices_for_ids(features: dict[str, Any], ids: list[str]) -> list[int]:
    lookup = {demo_id: idx for idx, demo_id in enumerate(features["demo_ids"])}
    return [lookup[demo_id] for demo_id in ids]


def _labels_for_ids(features: dict[str, Any], ids: list[str]) -> list[str]:
    lookup = {row["demo_id"]: row["label"] for row in features["rows"]}
    return [lookup[demo_id] for demo_id in ids]


def _demo_by_id(demos: list[FunctionalDemo], demo_id: str) -> FunctionalDemo:
    for demo in demos:
        if demo.demo_id == demo_id:
            return demo
    raise KeyError(demo_id)


def _mh_quality_map(handle: Any) -> dict[str, str]:
    quality = {}
    for label in ("worse", "okay", "better"):
        if label not in handle["mask"]:
            continue
        for raw in handle["mask"][label][()]:
            quality[_decode_key(raw)] = label
    return quality


def _mh_split_map(handle: Any) -> dict[str, str]:
    split_map = {}
    for label in ("worse", "better"):
        train_key = f"{label}_train"
        valid_key = f"{label}_valid"
        if train_key in handle["mask"]:
            for raw in handle["mask"][train_key][()]:
                split_map[_decode_key(raw)] = "train"
        if valid_key in handle["mask"]:
            for raw in handle["mask"][valid_key][()]:
                split_map[_decode_key(raw)] = "valid"
    return split_map


def _paired_split_map(handle: Any) -> dict[str, str]:
    if "mask" not in handle:
        return {}
    split_map = {}
    for key, value in (("train", "train"), ("valid", "valid")):
        if key in handle["mask"]:
            for raw in handle["mask"][key][()]:
                split_map[_decode_key(raw)] = value
    return split_map


def _mg_split(episode_id: str) -> str:
    return "valid" if _demo_index(episode_id) % 10 == 0 else "train"


def _decode_key(raw: Any) -> str:
    if isinstance(raw, bytes):
        return raw.decode("utf-8")
    return str(raw)


def _demo_index(key: str) -> int:
    tail = key.split("_")[-1]
    return int(tail)


def _reward_onset(rewards: np.ndarray) -> int | None:
    hits = np.flatnonzero(rewards > 0.0)
    if hits.size == 0:
        return None
    return int(hits[0])


def _first_true(values: np.ndarray) -> int | None:
    hits = np.flatnonzero(values)
    if hits.size == 0:
        return None
    return int(hits[0])


def _ratio(index: int | None, length: int) -> float:
    if index is None:
        return 1.0
    return float(index / max(1, length - 1))


def _path_length(values: np.ndarray) -> float:
    if values.shape[0] < 2:
        return 0.0
    return float(np.sum(np.linalg.norm(np.diff(values, axis=0), axis=1)))


def _turning_rate(velocity: np.ndarray) -> float:
    if velocity.shape[0] < 3:
        return 0.0
    norms = np.linalg.norm(velocity, axis=1)
    valid = norms > 1.0e-9
    unit = np.zeros_like(velocity)
    unit[valid] = velocity[valid] / norms[valid, None]
    cosines = np.sum(unit[1:] * unit[:-1], axis=1)
    turns = cosines < 0.0
    return float(np.mean(turns))


def _speed_minima_count(speed: np.ndarray) -> int:
    if speed.shape[0] < 3:
        return 0
    interior = speed[1:-1]
    return int(np.sum((interior < speed[:-2]) & (interior < speed[2:])))


def _sign_change_rate(values: np.ndarray) -> float:
    if values.shape[0] < 2:
        return 0.0
    signs = np.sign(values)
    changes = np.abs(np.diff(signs, axis=0)) > 0
    return float(np.mean(changes))


def _diag_log_variance(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    variance = np.var(values, axis=0) + 1.0e-8
    return float(np.sum(np.log(variance)))


def _random_predictions(train_labels: list[str], count: int, seed: int) -> list[str]:
    labels, counts = np.unique(np.asarray(train_labels), return_counts=True)
    probabilities = counts.astype(np.float64) / np.sum(counts)
    rng = np.random.default_rng(seed)
    return [str(label) for label in rng.choice(labels, size=count, p=probabilities)]


def _bad_label_for_target(target: dict[str, Any]) -> str:
    if target["label_kind"] == "quality":
        return "worse"
    return "failure"


def _mean(values: Iterable[float | None]) -> float | None:
    rows = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not rows:
        return None
    return float(np.mean(rows))


def _iqr(values: Iterable[float]) -> float:
    rows = np.asarray(list(values), dtype=np.float64)
    if rows.size == 0:
        return 0.0
    return float(np.percentile(rows, 75.0) - np.percentile(rows, 25.0))


def _zlib_matrix_bytes(matrix: np.ndarray) -> int:
    payload = matrix.astype(np.float32).tobytes()
    return len(zlib.compress(payload, level=9))


def _file_manifest(path: Path, task: str, family: str) -> dict[str, Any]:
    return {
        "task": task,
        "family": family,
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def _dataset_counts(demos: list[FunctionalDemo]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for demo in demos:
        key = f"{demo.family}/{demo.task}/{demo.split}/{demo.label}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _pad_width(values: np.ndarray, width: int) -> np.ndarray:
    if values.shape[1] >= width:
        return values[:, :width]
    pad = np.zeros((values.shape[0], width - values.shape[1]), dtype=values.dtype)
    return np.concatenate([values, pad], axis=1)


def _environment_payload() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def _source_hashes(repo_root: Path) -> dict[str, str]:
    paths = [
        repo_root / "src/zpe_robotics/functional_curation.py",
        repo_root / "src/zpe_robotics/schema.py",
        repo_root / "src/zpe_robotics/schema_baselines.py",
        repo_root / "src/zpe_robotics/schema_eval.py",
        repo_root / "pyproject.toml",
        repo_root / "uv.lock",
    ]
    return {str(path.relative_to(repo_root)): sha256_file(path) for path in paths if path.exists()}


def _write_failure_cases(
    failure_dir: Path,
    quality_eval: dict[str, Any],
    outliers: dict[str, Any],
    comparison: dict[str, Any],
) -> None:
    write_json(
        failure_dir / "classification_failures.json",
        {
            target_id: {
                method: payload["sample_failures"]
                for method, payload in result["methods"].items()
                if payload["sample_failures"]
            }
            for target_id, result in quality_eval["targets"].items()
        },
    )
    write_json(
        failure_dir / "outlier_failures.json",
        {
            target_id: {
                "best_baseline_method": result["best_baseline_method"],
                "primary_average_precision": result["primary_average_precision"],
                "best_baseline_average_precision": result["best_baseline_average_precision"],
            }
            for target_id, result in outliers["targets"].items()
            if not result["pass_vs_baselines"]
        },
    )
    lines = ["# Baseline Wins", ""]
    for target_id, row in sorted(comparison["target_results"].items()):
        if not row["beats_baselines"]:
            lines.append(
                f"- {target_id}: `{row['best_baseline_method']}` beat primary by "
                f"{-row['balanced_accuracy_margin']:.4f} balanced accuracy."
            )
    write_text(failure_dir / "baseline_wins.md", "\n".join(lines) + "\n")
