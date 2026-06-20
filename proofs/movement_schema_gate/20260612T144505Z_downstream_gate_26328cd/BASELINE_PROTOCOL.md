# Baseline Protocol

Baselines are frozen before scoring.

- DMP: external `movement_primitives.dmp.DMP`, trained per action on action trajectories.
- ProMP: external `movement_primitives.promp.ProMP`, trained per action on action trajectories.
- FMP: local Fourier movement primitive fallback, because no maintained FMP package is selected for this run.
- Exemplar memory: medoid/farthest selected raw demonstrations at fixed retained-demo budgets.
- Spectral selectors: FFT, DCT, and Fourier coefficient centrality selectors at the same budgets.
- Random controls: three deterministic seeds per budget.

All memory accounting includes retained-demo bytes. Schema-selected demos additionally include schema selector overhead.
