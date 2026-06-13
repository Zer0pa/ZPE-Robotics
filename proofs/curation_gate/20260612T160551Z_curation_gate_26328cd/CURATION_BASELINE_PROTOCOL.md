# Curation Baseline Protocol

## Dataset

- Primary dataset: RoboMimic v1.5 proficient-human low-dimensional Can, Lift, Square, Transport, and Tool Hang.
- Split policy: deterministic per-task train/validation/test freeze.
- No synthetic-only main proof is allowed.

## Search

- Query split: held-out test demonstrations.
- Candidate split: train demonstrations.
- Relevance: same task as query.
- Baselines: raw phase-aligned movement form, global PCA, FFT low-pass, DCT low-pass.
- Metric: truncated same-task mAP/P@k over real demonstrations.

## Representative Selection

- Budget: fixed demonstrations per task.
- ZPE method: task-conditioned movement-form basin center plus diversity.
- Baselines: random, mean central, raw medoid, raw medoid plus farthest-first k-center, PCA k-center.
- Metric: nearest selected same-task representative distance on validation+test demonstrations.

## Outliers

- Main labels: natural real-data silver labels from path length, endpoint displacement, velocity energy, and duration extremes inside each task.
- Baselines: raw distance threshold, kNN density/LOF-like score, random-projection isolation-like score.
- Metric: average precision against the review set. These are review flags, not automatic deletion.

## Gate

Pass requires at least two criteria, including at least one non-audit real-data baseline win. README claims remain frozen regardless of narrow product result.
