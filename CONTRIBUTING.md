# Contributing

ZPE-Robotics is a source-available product repo. Contributions are welcome when
they preserve the governing proof surface and the SAL v7.0 license boundary.

## Ground Rules

1. Open issues or pull requests against the public repo.
2. Keep changes scoped to one behavior, proof, or documentation surface.
3. Do not widen product claims without committed proof artifacts.
4. Do not replace blocker evidence with prose.
5. Do not change `LICENSE` or release workflow semantics without owner review.

## Local Check

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
python -m pytest tests -q
```

## Claim Discipline

Runtime and proof artifacts outrank prose. If a proposed change affects a README
metric, proof anchor, or blocker status, include the updated evidence artifact in
the same pull request.
