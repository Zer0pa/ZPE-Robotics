# Curation Prior Art

## Scope

Phase 06 treats ZPE-Robotics as a robot demonstration dataset curation/search/audit tool only. It does not claim broad movement memory or robot learning transfer.

## Existing Tools And Baselines

- RoboMimic already supplies standardized HDF5 demonstrations, low-dimensional observations/actions, dataset inspection scripts, filter keys, and training/evaluation workflows: https://robomimic.github.io/docs/datasets/overview.html
- LeRobot provides robot dataset metadata, loading, recording, visualization, and Hub distribution surfaces: https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3
- RLDS standardizes episodic reinforcement-learning datasets and tooling for loading, transforming, and sharing sequential decision data: https://github.com/google-research/rlds
- Robot Data Curation / DemInf is direct prior art for selecting useful robot demonstrations for imitation learning: https://www.roboticsproceedings.org/rss21/p023.pdf
- Data Quality in Imitation Learning is direct prior art for the effect of curated demonstration quality on policy performance: https://papers.neurips.cc/paper_files/paper/2023/file/fe692980c5d9732cf153ce27947653a7-Paper-Conference.pdf
- Trajectory similarity baselines include phase-aligned Euclidean distance, DTW, discrete Frechet-style path distance, PCA, FFT/DCT, and cluster-medoid/k-center selection.
- Outlier baselines include distance thresholds, Local Outlier Factor, Isolation Forest-style random partition/projection scores, and density/noise cluster labels.

## Decision Pressure

The local Phase 05 result is adverse to a broad product claim: the surviving result is `narrow_retrieval_curation_only`. Phase 06 may pass only as a narrow curation surface if it beats or usefully complements the real baselines on RoboMimic demonstrations.
