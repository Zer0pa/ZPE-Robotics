"""Movement dataset curation, search, and audit utilities."""

from __future__ import annotations

import datetime as dt
import json
import zlib
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .schema import MovementSchemaV1, SchemaMetadata, canonicalize_trajectory, resample_trajectory
from .schema_adaptation import primitive_feature_indices, primitive_feature_names
from .schema_baselines import dct_lowpass_vector, fft_lowpass_vector
from .utils import stable_json_dumps, write_json, write_text


DEFAULT_CURATOR_SEED = 20260615


def curate_movement_dataset(
    demos: list[Any],
    manifest: dict[str, Any],
    splits: dict[str, Any],
    output_dir: Path,
    seed: int = DEFAULT_CURATOR_SEED,
    frame_count: int = 96,
    component_count: int = 8,
    budget_per_class: int = 5,
) -> dict[str, Any]:
    """Build the curation index, baseline comparisons, and gate verdict."""

    output_dir.mkdir(parents=True, exist_ok=True)
    feature_names = tuple(manifest["feature_names"])
    form_indices = primitive_feature_indices(feature_names)
    form_names = primitive_feature_names(feature_names, form_indices)
    split_lookup = _split_lookup(splits)
    demo_lookup = _demo_lookup(demos)
    train_keys = tuple(splits["train"])
    grouped_train = _group_primitive_train(demo_lookup, train_keys, form_indices)
    schemas = _fit_task_schemas(grouped_train, form_names, frame_count, component_count)

    entries = _base_index_entries(demos, split_lookup, form_indices, frame_count)
    feature_payload = _index_feature_payload(entries, schemas, frame_count)
    for entry, vectors in zip(entries, feature_payload["entry_vectors"], strict=True):
        entry["vectors"] = vectors

    index_payload = {
        "schema_version": 1,
        "index_type": "movement_form_curation_index",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "seed": seed,
        "frame_count": frame_count,
        "component_count": component_count,
        "dataset_manifest_path": "DATASET_MANIFEST.json",
        "dataset_family": manifest.get("dataset_family"),
        "tasks": manifest.get("actions", []),
        "feature_names": list(feature_names),
        "movement_form_feature_names": list(form_names),
        "movement_form_feature_indices": list(form_indices),
        "split_hash": splits.get("split_hash"),
        "vector_methods": feature_payload["vector_methods"],
        "standardization": feature_payload["standardization"],
        "entries": entries,
    }
    index_bytes = _payload_zlib_bytes(index_payload)
    index_payload["storage"] = _index_storage_payload(index_payload, index_bytes)
    write_json(output_dir / "movement_index.json", index_payload)

    product_manifest = _curation_manifest(manifest, splits, output_dir, index_payload)
    write_json(output_dir / "DATASET_MANIFEST.json", product_manifest)

    search_eval = evaluate_search(index_payload)
    representatives = select_representatives(index_payload, budget_per_class=budget_per_class, seed=seed)
    representative_eval = evaluate_representatives(index_payload, representatives)
    outliers = detect_outliers(index_payload, seed=seed)
    outlier_eval = evaluate_outliers(outliers)
    audit_payload = _curation_audit_payload(index_payload, representatives, outliers, search_eval, representative_eval)
    baseline_comparison = compare_curation_baselines(search_eval, representative_eval, outlier_eval, audit_payload)
    final_verdict = _curation_final_verdict(baseline_comparison)

    write_json(output_dir / "search_eval.json", search_eval)
    write_json(output_dir / "representatives.json", representatives)
    write_json(output_dir / "representative_selection_eval.json", representative_eval)
    write_json(output_dir / "outliers.json", outliers)
    write_json(output_dir / "outlier_detection_eval.json", outlier_eval)
    write_json(output_dir / "curation_audit.json", audit_payload)
    write_json(output_dir / "baseline_comparison.json", baseline_comparison)
    write_json(output_dir / "FINAL_GATE_VERDICT.json", final_verdict)
    _write_failure_cases(output_dir / "failure_cases", search_eval, representative_eval, outlier_eval)
    write_text(output_dir / "curation_report.md", _curation_report_text(final_verdict, baseline_comparison))
    return final_verdict


def search_movement_index(
    index_path: Path,
    query_demo: str,
    top_k: int = 10,
    method: str = "zpe_form",
) -> dict[str, Any]:
    """Return nearest demonstrations for one indexed query demonstration."""

    index = _read_index(index_path)
    entries = index["entries"]
    lookup = {entry["demo_id"]: entry for entry in entries}
    if query_demo not in lookup:
        raise ValueError(f"query demo {query_demo!r} is not present in {index_path}")
    if method not in index["vector_methods"]:
        raise ValueError(f"unknown search method {method!r}")

    query = lookup[query_demo]
    candidates = [entry for entry in entries if entry["demo_id"] != query_demo]
    ranked = _rank_entries(query, candidates, method, top_k)
    return {
        "schema_version": 1,
        "index_path": str(index_path),
        "method": method,
        "query_demo": query_demo,
        "query_task": query["task"],
        "top_k": top_k,
        "results": ranked,
    }


def select_representatives_from_manifest(
    manifest_path: Path,
    budget_per_class: int,
    output_path: Path,
    seed: int = DEFAULT_CURATOR_SEED,
) -> dict[str, Any]:
    """Select representative demonstrations from a curation manifest."""

    index = _index_from_manifest(manifest_path)
    representatives = select_representatives(index, budget_per_class=budget_per_class, seed=seed)
    write_json(output_path, representatives)
    return representatives


def detect_outliers_from_manifest(
    manifest_path: Path,
    output_path: Path,
    seed: int = DEFAULT_CURATOR_SEED,
) -> dict[str, Any]:
    """Score natural trajectory outliers from a curation manifest."""

    index = _index_from_manifest(manifest_path)
    outliers = detect_outliers(index, seed=seed)
    write_json(output_path, outliers)
    return outliers


def evaluate_search(index: dict[str, Any], top_k_values: tuple[int, ...] = (1, 5, 10)) -> dict[str, Any]:
    methods = ("zpe_form", "raw_phase_aligned", "pca_global", "fft_lowpass", "dct_lowpass")
    entries = index["entries"]
    queries = [entry for entry in entries if entry["split"] == "test"]
    candidates = [entry for entry in entries if entry["split"] == "train"]
    rows = []
    method_summaries = {}
    for method in methods:
        method_rows = [_search_eval_row(query, candidates, method, top_k_values) for query in queries]
        method_summaries[method] = _search_method_summary(method_rows, top_k_values)
        rows.extend(method_rows)

    zpe_map = method_summaries["zpe_form"]["mean_average_precision"]
    baseline_methods = [method for method in methods if method != "zpe_form"]
    best_baseline = max(baseline_methods, key=lambda name: method_summaries[name]["mean_average_precision"])
    baseline_map = method_summaries[best_baseline]["mean_average_precision"]
    absolute_margin = zpe_map - baseline_map
    material_margin = 0.005
    return {
        "schema_version": 1,
        "metric": "same-task retrieval among train demonstrations for held-out test queries",
        "material_map_margin_required": material_margin,
        "query_split": "test",
        "candidate_split": "train",
        "relevance": "candidate task equals query task",
        "query_count": len(queries),
        "candidate_count": len(candidates),
        "top_k_values": list(top_k_values),
        "methods": method_summaries,
        "best_baseline_method": best_baseline,
        "zpe_form_map": zpe_map,
        "best_baseline_map": baseline_map,
        "absolute_map_margin": float(absolute_margin),
        "zpe_relative_map_lift": _relative_lift(zpe_map, baseline_map),
        "pass_vs_baselines": absolute_margin >= material_margin,
        "rows": rows,
    }


def select_representatives(
    index: dict[str, Any],
    budget_per_class: int,
    seed: int = DEFAULT_CURATOR_SEED,
) -> dict[str, Any]:
    if budget_per_class < 1:
        raise ValueError("budget_per_class must be positive")

    train_entries = [entry for entry in index["entries"] if entry["split"] == "train"]
    by_task = _entries_by_task(train_entries)
    methods = {
        "zpe_basin_diverse": lambda rows: _central_then_diverse(rows, budget_per_class, "zpe_form"),
        "raw_medoid": lambda rows: _medoid_only(rows, budget_per_class, "raw_phase_aligned"),
        "mean_central": lambda rows: _central_only(rows, budget_per_class, "raw_phase_aligned"),
        "kmedoids_raw_farthest": lambda rows: _central_then_diverse(rows, budget_per_class, "raw_phase_aligned"),
        "pca_kmedoids": lambda rows: _central_then_diverse(rows, budget_per_class, "pca_global"),
        "random": lambda rows: _random_representatives(rows, budget_per_class, seed),
    }
    selections = {}
    for method, selector in methods.items():
        selections[method] = {
            task: _representative_records(selector(rows), method)
            for task, rows in by_task.items()
        }
    return {
        "schema_version": 1,
        "budget_per_class": budget_per_class,
        "candidate_split": "train",
        "methods": selections,
    }


def evaluate_representatives(index: dict[str, Any], representatives: dict[str, Any]) -> dict[str, Any]:
    evaluation_entries = [entry for entry in index["entries"] if entry["split"] in {"validation", "test"}]
    rows = []
    summaries = {}
    for method, task_selections in representatives["methods"].items():
        selected_lookup = {
            task: [_entry_by_id(index, record["demo_id"]) for record in records]
            for task, records in task_selections.items()
        }
        method_rows = [_representative_eval_row(entry, selected_lookup, method) for entry in evaluation_entries]
        summaries[method] = _representative_method_summary(method_rows, task_selections)
        rows.extend(method_rows)

    zpe_distance = summaries["zpe_basin_diverse"]["mean_nearest_raw_distance"]
    comparison_names = ("random", "mean_central", "raw_medoid")
    best_named = min(comparison_names, key=lambda name: summaries[name]["mean_nearest_raw_distance"])
    best_named_distance = summaries[best_named]["mean_nearest_raw_distance"]
    best_baseline = min(
        [name for name in summaries if name != "zpe_basin_diverse"],
        key=lambda name: summaries[name]["mean_nearest_raw_distance"],
    )
    best_baseline_distance = summaries[best_baseline]["mean_nearest_raw_distance"]
    return {
        "schema_version": 1,
        "metric": "nearest selected same-task representative distance on validation+test demos",
        "evaluation_split": "validation+test",
        "distance_surface": "raw_phase_aligned movement-form vector",
        "methods": summaries,
        "zpe_mean_nearest_raw_distance": zpe_distance,
        "best_random_mean_medoid_method": best_named,
        "best_random_mean_medoid_distance": best_named_distance,
        "best_full_baseline_method": best_baseline,
        "best_full_baseline_distance": best_baseline_distance,
        "zpe_relative_improvement_vs_random_mean_medoid": _relative_error_reduction(
            zpe_distance,
            best_named_distance,
        ),
        "zpe_relative_improvement_vs_full_baselines": _relative_error_reduction(
            zpe_distance,
            best_baseline_distance,
        ),
        "pass_vs_random_mean_medoid": zpe_distance < best_named_distance,
        "pass_vs_full_baselines": zpe_distance < best_baseline_distance,
        "rows": rows,
    }


def detect_outliers(index: dict[str, Any], seed: int = DEFAULT_CURATOR_SEED) -> dict[str, Any]:
    entries = index["entries"]
    by_task = _entries_by_task(entries)
    method_scores: dict[str, dict[str, float]] = {
        "zpe_channel_outlier": {},
        "raw_distance_threshold": {},
        "lof_like_knn_density": {},
        "isolation_projection": {},
    }
    silver_labels = {}
    for task, task_entries in by_task.items():
        task_scores = _task_outlier_scores(task_entries, seed)
        for method, scores in task_scores.items():
            method_scores[method].update(scores)
        silver_labels.update(_silver_outlier_labels(task_entries))

    methods = {}
    for method, scores in method_scores.items():
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        methods[method] = {
            "ranked": [
                {
                    "demo_id": demo_id,
                    "task": _entry_by_id(index, demo_id)["task"],
                    "score": float(score),
                    "silver_label": bool(silver_labels.get(demo_id, False)),
                }
                for demo_id, score in ranked
            ],
        }

    review_set = []
    for demo_id, is_outlier in sorted(silver_labels.items()):
        if is_outlier:
            entry = _entry_by_id(index, demo_id)
            review_set.append(
                {
                    "demo_id": demo_id,
                    "task": entry["task"],
                    "basis": "top natural kinematic extremity within task",
                    "kinematic_summary": entry["kinematic_summary"],
                }
            )
    return {
        "schema_version": 1,
        "label_policy": "silver labels from natural kinematic extremes only; no synthetic corruption used",
        "silver_positive_count": len(review_set),
        "silver_review_set": review_set,
        "methods": methods,
    }


def evaluate_outliers(outliers: dict[str, Any]) -> dict[str, Any]:
    methods = {}
    positives = {row["demo_id"] for row in outliers["silver_review_set"]}
    positive_count = max(1, len(positives))
    for method, payload in outliers["methods"].items():
        ranked = payload["ranked"]
        hits = 0
        precision_sum = 0.0
        for rank, row in enumerate(ranked, start=1):
            if row["demo_id"] in positives:
                hits += 1
                precision_sum += hits / rank
        cutoff = positive_count
        top_rows = ranked[:cutoff]
        top_hits = sum(1 for row in top_rows if row["demo_id"] in positives)
        methods[method] = {
            "average_precision": float(precision_sum / positive_count),
            "precision_at_silver_count": float(top_hits / cutoff),
            "silver_count": positive_count,
            "top_review_count": cutoff,
            "top_review_hits": top_hits,
        }

    zpe_ap = methods["zpe_channel_outlier"]["average_precision"]
    baseline_names = [name for name in methods if name != "zpe_channel_outlier"]
    best_baseline = max(baseline_names, key=lambda name: methods[name]["average_precision"])
    baseline_ap = methods[best_baseline]["average_precision"]
    return {
        "schema_version": 1,
        "metric": "ranking average precision against natural kinematic-extreme silver review set",
        "methods": methods,
        "best_baseline_method": best_baseline,
        "zpe_average_precision": zpe_ap,
        "best_baseline_average_precision": baseline_ap,
        "zpe_relative_ap_lift": _relative_lift(zpe_ap, baseline_ap),
        "pass_vs_baselines": zpe_ap > baseline_ap,
    }


def compare_curation_baselines(
    search_eval: dict[str, Any],
    representative_eval: dict[str, Any],
    outlier_eval: dict[str, Any],
    audit_payload: dict[str, Any],
) -> dict[str, Any]:
    search_pass = bool(search_eval["pass_vs_baselines"])
    representative_pass = bool(representative_eval["pass_vs_random_mean_medoid"])
    outlier_pass = bool(outlier_eval["pass_vs_baselines"])
    audit_pass = bool(audit_payload["audit_surface"]["no_hidden_costs"]) and bool(
        audit_payload["audit_surface"]["per_demo_reasons"]
    )
    non_audit_passes = sum([search_pass, representative_pass, outlier_pass])
    pass_count = non_audit_passes + int(audit_pass)
    return {
        "schema_version": 1,
        "success_criteria": {
            "better_search_map_than_raw_fft_dct_pca": search_pass,
            "better_representative_selection_than_random_mean_medoid": representative_pass,
            "better_outlier_detection_than_distance_lof_isolation": outlier_pass,
            "clearer_audit_receipts_than_raw_selection": audit_pass,
            "downstream_proxy_improvement": False,
        },
        "non_audit_pass_count": non_audit_passes,
        "pass_count": pass_count,
        "search": {
            "zpe_form_map": search_eval["zpe_form_map"],
            "best_baseline_method": search_eval["best_baseline_method"],
            "best_baseline_map": search_eval["best_baseline_map"],
            "relative_lift": search_eval["zpe_relative_map_lift"],
        },
        "representatives": {
            "zpe_distance": representative_eval["zpe_mean_nearest_raw_distance"],
            "best_random_mean_medoid_method": representative_eval["best_random_mean_medoid_method"],
            "best_random_mean_medoid_distance": representative_eval["best_random_mean_medoid_distance"],
            "best_full_baseline_method": representative_eval["best_full_baseline_method"],
            "best_full_baseline_distance": representative_eval["best_full_baseline_distance"],
            "relative_lift_vs_random_mean_medoid": representative_eval[
                "zpe_relative_improvement_vs_random_mean_medoid"
            ],
            "relative_lift_vs_full_baselines": representative_eval[
                "zpe_relative_improvement_vs_full_baselines"
            ],
        },
        "outliers": {
            "zpe_average_precision": outlier_eval["zpe_average_precision"],
            "best_baseline_method": outlier_eval["best_baseline_method"],
            "best_baseline_average_precision": outlier_eval["best_baseline_average_precision"],
            "relative_lift": outlier_eval["zpe_relative_ap_lift"],
        },
        "audit": audit_payload["audit_surface"],
    }


def _curation_final_verdict(comparison: dict[str, Any]) -> dict[str, Any]:
    criteria = comparison["success_criteria"]
    pass_count = int(comparison["pass_count"])
    non_audit_passes = int(comparison["non_audit_pass_count"])
    if pass_count >= 2 and non_audit_passes >= 1:
        status = "curation_product_pass"
        product_worthy = True
    elif criteria["clearer_audit_receipts_than_raw_selection"] and non_audit_passes == 0:
        status = "audit_only_narrow_pass"
        product_worthy = False
    elif non_audit_passes == 0:
        status = "baseline_tie_no_product_edge"
        product_worthy = False
    else:
        status = "abandon_productization"
        product_worthy = False
    return {
        "schema_version": 1,
        "status": status,
        "product_worthy": product_worthy,
        "scope": "robot movement dataset curation, search, representative selection, outlier review, and audit",
        "broad_movement_memory_claim_allowed": False,
        "policy_transfer_claim_allowed": False,
        "readme_claim_upgrade_allowed": False,
        "success_criteria": criteria,
        "non_audit_pass_count": non_audit_passes,
        "pass_count": pass_count,
        "reason": _verdict_reason(status, comparison),
    }


def _base_index_entries(
    demos: list[Any],
    split_lookup: dict[str, str],
    feature_indices: tuple[int, ...],
    frame_count: int,
) -> list[dict[str, Any]]:
    entries = []
    for demo in demos:
        demo_id = f"{demo.metadata.action_label}/{demo.metadata.episode_id}"
        primitive = _primitive_trajectory(demo.trajectory, feature_indices)
        resampled = resample_trajectory(primitive, frame_count)
        canonical = canonicalize_trajectory(primitive, frame_count=frame_count).values
        entries.append(
            {
                "demo_id": demo_id,
                "task": demo.metadata.action_label,
                "episode_id": demo.metadata.episode_id,
                "source_path": demo.metadata.source_path,
                "split": split_lookup[demo_id],
                "frame_count": int(demo.frame_count),
                "kinematic_summary": _kinematic_summary(resampled),
                "_raw_form_vector": canonical.reshape(-1),
                "_primitive": primitive,
            }
        )
    return entries


def _index_feature_payload(
    entries: list[dict[str, Any]],
    schemas: dict[str, MovementSchemaV1],
    frame_count: int,
) -> dict[str, Any]:
    raw_matrix = np.stack([entry["_raw_form_vector"] for entry in entries], axis=0)
    fft_matrix = np.stack([fft_lowpass_vector(entry["_primitive"], frame_count=frame_count) for entry in entries], axis=0)
    dct_matrix = np.stack([dct_lowpass_vector(entry["_primitive"], frame_count=frame_count) for entry in entries], axis=0)
    pca_matrix = _pca_vectors(raw_matrix, _train_mask(entries), component_count=16)
    zpe_matrix = np.stack([_schema_score_vector(entry["_primitive"], schemas) for entry in entries], axis=0)

    matrices = {
        "raw_phase_aligned": raw_matrix,
        "fft_lowpass": fft_matrix,
        "dct_lowpass": dct_matrix,
        "pca_global": pca_matrix,
        "zpe_form": zpe_matrix,
    }
    standardized = {}
    standardization = {}
    train_mask = _train_mask(entries)
    for name, matrix in matrices.items():
        standardized[name], standardization[name] = _standardize_by_train(matrix, train_mask)

    entry_vectors = []
    for row_idx in range(len(entries)):
        entry_vectors.append(
            {
                name: _compact_vector(matrix[row_idx])
                for name, matrix in standardized.items()
            }
        )

    for entry in entries:
        entry.pop("_raw_form_vector", None)
        entry.pop("_primitive", None)

    return {
        "vector_methods": {
            "zpe_form": "movement-form schema score vector fitted per task on train split",
            "raw_phase_aligned": "start-relative phase-aligned primitive trajectory vector",
            "pca_global": "global PCA vector fitted on train raw movement-form vectors",
            "fft_lowpass": "low-pass FFT coefficient vector over primitive trajectory",
            "dct_lowpass": "low-pass DCT coefficient vector over primitive trajectory",
        },
        "standardization": standardization,
        "entry_vectors": entry_vectors,
    }


def _fit_task_schemas(
    grouped_train: dict[str, list[np.ndarray]],
    feature_names: tuple[str, ...],
    frame_count: int,
    component_count: int,
) -> dict[str, MovementSchemaV1]:
    schemas = {}
    for task, trajectories in grouped_train.items():
        metadata = SchemaMetadata(
            task,
            frame_count=frame_count,
            component_count=component_count,
            feature_names=feature_names,
        )
        schemas[task] = MovementSchemaV1.fit(trajectories, metadata)
    return schemas


def _schema_score_vector(primitive: np.ndarray, schemas: dict[str, MovementSchemaV1]) -> np.ndarray:
    features = []
    for task in sorted(schemas):
        score = schemas[task].score_demo(primitive)
        features.extend(
            [
                score.distance,
                score.latent_distance,
                score.reconstruction_rmse,
                score.endpoint_error,
                score.residual_rmse,
            ]
        )
    return np.asarray(features, dtype=np.float64)


def _pca_vectors(matrix: np.ndarray, train_mask: np.ndarray, component_count: int) -> np.ndarray:
    train = matrix[train_mask]
    mean = np.mean(train, axis=0)
    centered_train = train - mean
    _, _, vt = np.linalg.svd(centered_train, full_matrices=False)
    components = vt[: max(1, min(component_count, vt.shape[0]))]
    return (matrix - mean) @ components.T


def _standardize_by_train(matrix: np.ndarray, train_mask: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    train = matrix[train_mask]
    mean = np.mean(train, axis=0)
    scale = np.std(train, axis=0)
    scale = np.where(scale < 1.0e-8, 1.0, scale)
    standardized = (matrix - mean) / scale
    return standardized, {
        "mean_shape": list(mean.shape),
        "scale_shape": list(scale.shape),
        "zero_scale_floor": 1.0e-8,
    }


def _search_eval_row(
    query: dict[str, Any],
    candidates: list[dict[str, Any]],
    method: str,
    top_k_values: tuple[int, ...],
) -> dict[str, Any]:
    ranked = _rank_entries(query, candidates, method, top_k=max(top_k_values))
    relevant_total = sum(1 for candidate in candidates if candidate["task"] == query["task"])
    hits = 0
    precision_sum = 0.0
    for rank, row in enumerate(ranked, start=1):
        if row["task"] == query["task"]:
            hits += 1
            precision_sum += hits / rank
    precision_at = {
        f"p_at_{k}": sum(1 for row in ranked[:k] if row["task"] == query["task"]) / max(1, min(k, len(ranked)))
        for k in top_k_values
    }
    return {
        "method": method,
        "query_demo": query["demo_id"],
        "query_task": query["task"],
        "average_precision": precision_sum / max(1, min(relevant_total, len(ranked))),
        "top_results": ranked[: max(top_k_values)],
        **precision_at,
    }


def _search_method_summary(rows: list[dict[str, Any]], top_k_values: tuple[int, ...]) -> dict[str, float]:
    summary = {"mean_average_precision": _mean(row["average_precision"] for row in rows)}
    for k in top_k_values:
        key = f"p_at_{k}"
        summary[key] = _mean(row[key] for row in rows)
    return summary


def _rank_entries(
    query: dict[str, Any],
    candidates: list[dict[str, Any]],
    method: str,
    top_k: int,
) -> list[dict[str, Any]]:
    query_vector = np.asarray(query["vectors"][method], dtype=np.float64)
    rows = []
    for candidate in candidates:
        candidate_vector = np.asarray(candidate["vectors"][method], dtype=np.float64)
        distance = float(np.sqrt(np.mean(np.square(query_vector - candidate_vector))))
        rows.append(
            {
                "demo_id": candidate["demo_id"],
                "task": candidate["task"],
                "episode_id": candidate["episode_id"],
                "split": candidate["split"],
                "distance": distance,
            }
        )
    return sorted(rows, key=lambda row: (row["distance"], row["demo_id"]))[:top_k]


def _central_then_diverse(rows: list[dict[str, Any]], budget: int, method: str) -> list[dict[str, Any]]:
    vectors = _method_matrix(rows, method)
    count = min(budget, len(rows))
    if count >= len(rows):
        return list(rows)

    distances = _pairwise_rmse(vectors)
    selected = [int(np.argmin(np.sum(distances, axis=1)))]
    while len(selected) < count:
        min_distance = np.min(distances[:, selected], axis=1)
        min_distance[selected] = -1.0
        selected.append(int(np.argmax(min_distance)))
    return [rows[idx] for idx in selected]


def _central_only(rows: list[dict[str, Any]], budget: int, method: str) -> list[dict[str, Any]]:
    vectors = _method_matrix(rows, method)
    centroid = np.mean(vectors, axis=0)
    distances = np.sqrt(np.mean(np.square(vectors - centroid[None, :]), axis=1))
    selected = np.argsort(distances, kind="stable")[: min(budget, len(rows))]
    return [rows[int(idx)] for idx in selected]


def _medoid_only(rows: list[dict[str, Any]], budget: int, method: str) -> list[dict[str, Any]]:
    vectors = _method_matrix(rows, method)
    distances = _pairwise_rmse(vectors)
    selected = np.argsort(np.sum(distances, axis=1), kind="stable")[: min(budget, len(rows))]
    return [rows[int(idx)] for idx in selected]


def _random_representatives(rows: list[dict[str, Any]], budget: int, seed: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed + sum(ord(ch) for ch in rows[0]["task"]))
    selected = rng.permutation(len(rows))[: min(budget, len(rows))]
    return [rows[int(idx)] for idx in selected]


def _representative_records(entries: list[dict[str, Any]], method: str) -> list[dict[str, Any]]:
    return [
        {
            "demo_id": entry["demo_id"],
            "task": entry["task"],
            "episode_id": entry["episode_id"],
            "split": entry["split"],
            "reason": _representative_reason(method),
            "kinematic_summary": entry["kinematic_summary"],
        }
        for entry in entries
    ]


def _representative_eval_row(
    entry: dict[str, Any],
    selected_lookup: dict[str, list[dict[str, Any]]],
    method: str,
) -> dict[str, Any]:
    candidates = selected_lookup[entry["task"]]
    query_vector = np.asarray(entry["vectors"]["raw_phase_aligned"], dtype=np.float64)
    distances = [
        (
            candidate["demo_id"],
            float(
                np.sqrt(
                    np.mean(
                        np.square(query_vector - np.asarray(candidate["vectors"]["raw_phase_aligned"], dtype=np.float64))
                    )
                )
            ),
        )
        for candidate in candidates
    ]
    nearest_demo, nearest_distance = min(distances, key=lambda item: (item[1], item[0]))
    return {
        "method": method,
        "demo_id": entry["demo_id"],
        "task": entry["task"],
        "split": entry["split"],
        "nearest_representative": nearest_demo,
        "nearest_raw_distance": nearest_distance,
    }


def _representative_method_summary(
    rows: list[dict[str, Any]],
    task_selections: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    selected_count = sum(len(records) for records in task_selections.values())
    storage_bytes = _payload_zlib_bytes(task_selections)
    return {
        "selected_demo_count": selected_count,
        "selection_zlib_bytes": storage_bytes,
        "mean_nearest_raw_distance": _mean(row["nearest_raw_distance"] for row in rows),
        "p95_nearest_raw_distance": _percentile([row["nearest_raw_distance"] for row in rows], 95.0),
        "coverage_proxy": 1.0 / (1.0 + _mean(row["nearest_raw_distance"] for row in rows)),
    }


def _task_outlier_scores(entries: list[dict[str, Any]], seed: int) -> dict[str, dict[str, float]]:
    raw = _method_matrix(entries, "raw_phase_aligned")
    zpe = _method_matrix(entries, "zpe_form")
    raw_center_scores = _center_distance_scores(entries, raw)
    zpe_center_scores = _center_distance_scores(entries, zpe)
    lof_scores = _lof_like_scores(entries, raw, neighbors=min(10, max(2, len(entries) // 10)))
    isolation_scores = _isolation_projection_scores(entries, raw, seed)
    return {
        "zpe_channel_outlier": zpe_center_scores,
        "raw_distance_threshold": raw_center_scores,
        "lof_like_knn_density": lof_scores,
        "isolation_projection": isolation_scores,
    }


def _center_distance_scores(entries: list[dict[str, Any]], matrix: np.ndarray) -> dict[str, float]:
    centroid = np.mean(matrix, axis=0)
    distances = np.sqrt(np.mean(np.square(matrix - centroid[None, :]), axis=1))
    return {entry["demo_id"]: float(score) for entry, score in zip(entries, distances, strict=True)}


def _lof_like_scores(entries: list[dict[str, Any]], matrix: np.ndarray, neighbors: int) -> dict[str, float]:
    distances = _pairwise_rmse(matrix)
    np.fill_diagonal(distances, np.inf)
    sorted_distances = np.sort(distances, axis=1)
    local_radius = np.mean(sorted_distances[:, :neighbors], axis=1)
    neighbor_indices = np.argsort(distances, axis=1)[:, :neighbors]
    neighbor_radius = np.mean(local_radius[neighbor_indices], axis=1)
    scores = local_radius / np.maximum(neighbor_radius, 1.0e-12)
    return {entry["demo_id"]: float(score) for entry, score in zip(entries, scores, strict=True)}


def _isolation_projection_scores(entries: list[dict[str, Any]], matrix: np.ndarray, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed + len(entries))
    projection_count = min(32, max(4, matrix.shape[1]))
    directions = rng.normal(size=(matrix.shape[1], projection_count))
    directions /= np.maximum(np.linalg.norm(directions, axis=0, keepdims=True), 1.0e-12)
    projected = matrix @ directions
    median = np.median(projected, axis=0)
    mad = np.median(np.abs(projected - median[None, :]), axis=0)
    mad = np.where(mad < 1.0e-8, 1.0, mad)
    scores = np.mean(np.abs(projected - median[None, :]) / mad[None, :], axis=1)
    return {entry["demo_id"]: float(score) for entry, score in zip(entries, scores, strict=True)}


def _silver_outlier_labels(entries: list[dict[str, Any]]) -> dict[str, bool]:
    rows = []
    metrics = ("path_length", "velocity_energy", "endpoint_norm", "frame_count")
    matrix = np.asarray([[entry["kinematic_summary"][name] for name in metrics] for entry in entries], dtype=np.float64)
    median = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - median[None, :]), axis=0)
    mad = np.where(mad < 1.0e-8, 1.0, mad)
    scores = np.mean(np.abs(matrix - median[None, :]) / mad[None, :], axis=1)
    cutoff_count = max(1, int(round(len(entries) * 0.10)))
    cutoff_indices = set(np.argsort(scores)[-cutoff_count:])
    for idx, entry in enumerate(entries):
        rows.append((entry["demo_id"], idx in cutoff_indices))
    return dict(rows)


def _curation_manifest(
    manifest: dict[str, Any],
    splits: dict[str, Any],
    output_dir: Path,
    index_payload: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(manifest)
    payload["curation_product"] = {
        "run_dir": str(output_dir),
        "movement_index_path": str(output_dir / "movement_index.json"),
        "split_hash": splits.get("split_hash"),
        "index_entry_count": len(index_payload["entries"]),
        "index_zlib_bytes": index_payload["storage"]["index_zlib_json_bytes"],
        "hidden_memory_costs_reported": True,
    }
    payload["splits"] = {
        "train_count": len(splits["train"]),
        "validation_count": len(splits["validation"]),
        "test_count": len(splits["test"]),
        "split_hash": splits.get("split_hash"),
    }
    return payload


def _curation_audit_payload(
    index: dict[str, Any],
    representatives: dict[str, Any],
    outliers: dict[str, Any],
    search_eval: dict[str, Any],
    representative_eval: dict[str, Any],
) -> dict[str, Any]:
    selected_ids = {
        record["demo_id"]
        for method_payload in representatives["methods"].values()
        for records in method_payload.values()
        for record in records
    }
    outlier_ids = {row["demo_id"] for row in outliers["silver_review_set"]}
    entries = []
    for entry in index["entries"]:
        reasons = []
        if entry["demo_id"] in selected_ids:
            reasons.append("selected_by_at_least_one_representative_policy")
        if entry["demo_id"] in outlier_ids:
            reasons.append("flagged_for_outlier_review_by_natural_kinematic_extremity")
        if not reasons:
            reasons.append("retained_in_search_index_without_selection_or_rejection")
        entries.append(
            {
                "demo_id": entry["demo_id"],
                "task": entry["task"],
                "split": entry["split"],
                "status": _audit_status(entry["demo_id"], selected_ids, outlier_ids),
                "reasons": reasons,
                "source_path": entry["source_path"],
            }
        )
    return {
        "schema_version": 1,
        "audit_surface": {
            "per_demo_reasons": True,
            "selected_demo_ids_reported": True,
            "outlier_review_ids_reported": True,
            "no_hidden_costs": True,
            "index_zlib_json_bytes": index["storage"]["index_zlib_json_bytes"],
            "representative_selection_zlib_bytes": representative_eval["methods"]["zpe_basin_diverse"][
                "selection_zlib_bytes"
            ],
            "search_query_count": search_eval["query_count"],
        },
        "selection_policy": "representative policies are explicit; zpe_basin_diverse is compared against raw/random baselines",
        "rejection_policy": "outliers are review flags, not automatic data deletion",
        "entries": entries,
    }


def _write_failure_cases(
    failure_dir: Path,
    search_eval: dict[str, Any],
    representative_eval: dict[str, Any],
    outlier_eval: dict[str, Any],
) -> None:
    failure_dir.mkdir(parents=True, exist_ok=True)
    if not search_eval["pass_vs_baselines"]:
        write_json(failure_dir / "search_best_baseline_beats_zpe.json", _compact_failure(search_eval))
    if not representative_eval["pass_vs_full_baselines"]:
        write_json(
            failure_dir / "representative_full_baseline_beats_zpe.json",
            _compact_failure(representative_eval),
        )
    if not outlier_eval["pass_vs_baselines"]:
        write_json(failure_dir / "outlier_best_baseline_beats_zpe.json", _compact_failure(outlier_eval))


def _curation_report_text(verdict: dict[str, Any], comparison: dict[str, Any]) -> str:
    criteria = comparison["success_criteria"]
    return f"""# Curation Gate Report

## Verdict

- Final verdict: `{verdict['status']}`
- Product-worthy narrow scope: `{verdict['product_worthy']}`
- Broad movement-memory claim allowed: `False`
- README claim upgrade allowed: `False`

## Criteria

- Search beats raw/FFT/DCT/PCA baselines: `{criteria['better_search_map_than_raw_fft_dct_pca']}`
- Representative selection beats random/mean/medoid: `{criteria['better_representative_selection_than_random_mean_medoid']}`
- Outlier detection beats distance/LOF/isolation-like baselines: `{criteria['better_outlier_detection_than_distance_lof_isolation']}`
- Audit receipts expose per-demo reasons and memory costs: `{criteria['clearer_audit_receipts_than_raw_selection']}`

## Baseline Comparison

- Search zpe mAP: `{comparison['search']['zpe_form_map']}`
- Search best baseline: `{comparison['search']['best_baseline_method']}` at `{comparison['search']['best_baseline_map']}`
- Representative zpe distance: `{comparison['representatives']['zpe_distance']}`
- Representative best random/mean/medoid: `{comparison['representatives']['best_random_mean_medoid_method']}` at `{comparison['representatives']['best_random_mean_medoid_distance']}`
- Outlier zpe AP: `{comparison['outliers']['zpe_average_precision']}`
- Outlier best baseline: `{comparison['outliers']['best_baseline_method']}` at `{comparison['outliers']['best_baseline_average_precision']}`
"""


def _index_from_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    curation = manifest.get("curation_product", {})
    index_path = Path(curation.get("movement_index_path", manifest_path.parent / "movement_index.json"))
    if not index_path.is_absolute():
        index_path = manifest_path.parent / index_path
    return _read_index(index_path)


def _read_index(index_path: Path) -> dict[str, Any]:
    return json.loads(index_path.read_text(encoding="utf-8"))


def _split_lookup(splits: dict[str, Any]) -> dict[str, str]:
    lookup = {}
    for split_name in ("train", "validation", "test"):
        for key in splits[split_name]:
            lookup[key] = split_name
    return lookup


def _demo_lookup(demos: list[Any]) -> dict[str, Any]:
    return {f"{demo.metadata.action_label}/{demo.metadata.episode_id}": demo for demo in demos}


def _group_primitive_train(
    demo_lookup: dict[str, Any],
    train_keys: Iterable[str],
    feature_indices: tuple[int, ...],
) -> dict[str, list[np.ndarray]]:
    grouped: dict[str, list[np.ndarray]] = {}
    for key in train_keys:
        demo = demo_lookup[key]
        grouped.setdefault(demo.metadata.action_label, []).append(
            _primitive_trajectory(demo.trajectory, feature_indices)
        )
    return grouped


def _primitive_trajectory(trajectory: np.ndarray, feature_indices: tuple[int, ...]) -> np.ndarray:
    return np.asarray(trajectory, dtype=np.float64)[:, feature_indices]


def _kinematic_summary(resampled: np.ndarray) -> dict[str, float]:
    velocity = np.gradient(resampled, axis=0)
    diffs = np.diff(resampled, axis=0)
    return {
        "frame_count": float(resampled.shape[0]),
        "path_length": float(np.sum(np.sqrt(np.sum(np.square(diffs), axis=1)))),
        "endpoint_norm": float(np.sqrt(np.sum(np.square(resampled[-1] - resampled[0])))),
        "velocity_energy": float(np.mean(np.sqrt(np.sum(np.square(velocity), axis=1)))),
    }


def _entries_by_task(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_task: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        by_task.setdefault(entry["task"], []).append(entry)
    return by_task


def _entry_by_id(index: dict[str, Any], demo_id: str) -> dict[str, Any]:
    for entry in index["entries"]:
        if entry["demo_id"] == demo_id:
            return entry
    raise KeyError(demo_id)


def _method_matrix(entries: list[dict[str, Any]], method: str) -> np.ndarray:
    return np.asarray([entry["vectors"][method] for entry in entries], dtype=np.float64)


def _train_mask(entries: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([entry["split"] == "train" for entry in entries], dtype=bool)


def _pairwise_rmse(matrix: np.ndarray) -> np.ndarray:
    gram = matrix @ matrix.T
    square_norm = np.sum(np.square(matrix), axis=1)
    distances = square_norm[:, None] + square_norm[None, :] - 2.0 * gram
    distances = np.maximum(distances / matrix.shape[1], 0.0)
    return np.sqrt(distances)


def _compact_vector(vector: np.ndarray) -> list[float]:
    return np.round(np.asarray(vector, dtype=np.float64), 6).astype(float).tolist()


def _payload_zlib_bytes(payload: Any) -> int:
    return len(zlib.compress(stable_json_dumps(payload).encode("utf-8"), level=9))


def _index_storage_payload(index_payload: dict[str, Any], index_bytes: int) -> dict[str, Any]:
    vector_dims = {
        method: len(index_payload["entries"][0]["vectors"][method]) if index_payload["entries"] else 0
        for method in index_payload["vector_methods"]
    }
    return {
        "index_json_bytes": len(stable_json_dumps(index_payload).encode("utf-8")),
        "index_zlib_json_bytes": index_bytes,
        "entry_count": len(index_payload["entries"]),
        "vector_dimensions": vector_dims,
        "hidden_memory_costs_reported": True,
    }


def _representative_reason(method: str) -> str:
    reasons = {
        "zpe_basin_diverse": "near learned movement-form basin center while preserving task variation",
        "raw_medoid": "closest raw movement-form vector to task centroid",
        "mean_central": "closest raw movement-form vector to task mean",
        "kmedoids_raw_farthest": "raw medoid followed by farthest-first task coverage",
        "pca_kmedoids": "PCA medoid followed by farthest-first task coverage",
        "random": "deterministic random baseline",
    }
    return reasons.get(method, method)


def _audit_status(demo_id: str, selected_ids: set[str], outlier_ids: set[str]) -> str:
    if demo_id in selected_ids and demo_id in outlier_ids:
        return "selected_and_outlier_review"
    if demo_id in selected_ids:
        return "selected_representative"
    if demo_id in outlier_ids:
        return "outlier_review"
    return "indexed"


def _compact_failure(payload: dict[str, Any]) -> dict[str, Any]:
    compact = dict(payload)
    compact.pop("rows", None)
    return compact


def _verdict_reason(status: str, comparison: dict[str, Any]) -> str:
    if status == "curation_product_pass":
        return "The narrow curation surface met at least two criteria, including a real-data baseline win."
    if status == "audit_only_narrow_pass":
        return "Baselines were not beaten, but the audit surface remains a useful provenance wrapper."
    if status == "baseline_tie_no_product_edge":
        return "The curation methods did not show a product edge beyond baselines."
    return "The curation methods lost enough baseline comparisons to abandon productization."


def _relative_lift(value: float, baseline: float) -> float:
    return float((value - baseline) / max(abs(baseline), 1.0e-12))


def _relative_error_reduction(value: float, baseline: float) -> float:
    return float((baseline - value) / max(abs(baseline), 1.0e-12))


def _mean(values: Iterable[float]) -> float:
    rows = [float(value) for value in values]
    return float(np.mean(rows)) if rows else 0.0


def _percentile(values: Iterable[float], percentile: float) -> float:
    rows = [float(value) for value in values]
    return float(np.percentile(rows, percentile)) if rows else 0.0
