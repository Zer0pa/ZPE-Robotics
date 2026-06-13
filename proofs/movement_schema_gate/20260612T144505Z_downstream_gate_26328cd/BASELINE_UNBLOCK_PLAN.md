# Baseline Unblock Plan

Decision: use maintained DMP/ProMP package baselines where available and a scoped local Fourier fallback for FMP.

Unblock attempts:

1. Maintained package integration: `movement-primitives` with versions `{'movement-primitives': '0.9.1', 'pytransform3d': '3.15.0', 'scipy': '1.17.1'}`.
2. Reviewed minimal implementation: local Fourier movement primitive fallback for FMP only.
3. Reduced-but-valid protocol: action-space start/goal adaptation and held-out action RMSE on the frozen RoboMimic split.

No zstd/gzip/FFT/DCT baseline is used as a substitute for DMP/ProMP/FMP.
