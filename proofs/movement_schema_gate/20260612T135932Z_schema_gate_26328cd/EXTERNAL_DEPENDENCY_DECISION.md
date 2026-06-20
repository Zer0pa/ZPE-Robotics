# External Dependency Decision

Decision: use the existing project `.venv` and install benchmark-only external movement-primitive dependencies there for this blocker-resolution run.

The dependency is not part of the runtime archive surface. It is used only to produce DMP/ProMP generation/adaptation pressure receipts.

```json
{
  "movement-primitives": "0.9.1",
  "pytransform3d": "3.15.0",
  "scipy": "1.17.1"
}
```

FMP remains a local Fourier movement-primitive generation baseline in this run because no maintained external FMP package was selected.
