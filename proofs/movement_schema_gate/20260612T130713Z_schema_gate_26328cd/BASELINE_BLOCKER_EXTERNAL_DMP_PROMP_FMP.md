# External DMP / ProMP / FMP Baseline Blocker

Status: `blocked_external_generation_adaptation`

The run did not execute a generation/adaptation-capable external DMP, ProMP, or FMP implementation.
Local coefficient wrappers remain recorded in `baseline_metrics.json`, but they are retrieval proxies only.

## Checked Packages

```json
{
  "movement_primitives": false,
  "promp": false,
  "pydmps": false
}
```

## Required To Unblock

- Select and pin a maintained movement-primitive package or vendor a reviewed implementation.
- Define start/goal perturbation and generation/adaptation metrics before seeing results.
- Run the external baselines on the same frozen split and write generation/adaptation errors.
