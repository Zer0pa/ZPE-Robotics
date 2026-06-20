# Falsification Memo

## Verdict

`pressure_gate_failed_sovereign_incomplete`

Sovereign gate pass: `False`.
README claim upgrade allowed: `False`.

## Retrieval Floor

- schema accuracy: `1.0`
- Can margin mean: `0.2181864411825071`

## Nearest-Demo Pressure

```json
{
  "equal_or_lower_memory_exemplar_match_exists": true,
  "limitation": "A memory-pressure pass floor is not a sovereign pass without external movement-primitive generation/adaptation and transfer/adaptation evidence.",
  "memory_pressure_pass_floor": false,
  "schema_ties_or_beats_all_demo_accuracy": true,
  "schema_uses_less_memory_than_all_demo_zlib": true
}
```

## MDL / Rate-Distortion

- formula frozen before final verdict: `True`
- best component count by description score: `1`

## Blockers

- external DMP/ProMP/FMP generation/adaptation status: `blocked_external_generation_adaptation`
- downstream imitation or policy adaptation: blocked; see `TRANSFER_BLOCKER.md`

## Decision

Do not upgrade README claims. Continue only through a future adaptation/generation-capable baseline gate, or narrow the public claim to archive/retrieval plus the specific pressure receipts emitted here.
