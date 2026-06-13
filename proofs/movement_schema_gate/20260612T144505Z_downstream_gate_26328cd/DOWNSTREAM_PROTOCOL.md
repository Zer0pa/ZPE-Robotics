# Downstream Utility Protocol

Primary metric: held-out action imitation RMSE, lower is better.

Task: select or generate an action trajectory for each held-out demonstration's true action label. The predictor is not allowed to use the held-out trajectory except for start/goal conditioning in the adaptation subtest.

Subtests:

1. Demo-selection utility: schema-selected training demonstrations are averaged into a phase-conditioned action predictor and compared with random, nearest-demo, raw-all, FFT, DCT, and FMP selectors at identical budgets.
2. Action-space adaptation: ZPE schema initializer, mean endpoint adaptation, medoid endpoint adaptation, FMP, external DMP, and external ProMP generate action trajectories under the same frozen split.

This is an imitation/adaptation proxy, not live policy transfer or robot execution. No README claim upgrade is allowed from this run.
