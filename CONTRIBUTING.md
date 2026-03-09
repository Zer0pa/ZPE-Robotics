# Contributing

This repo is private staged and evidence-first.

## Ground Rules

- negative findings are first-class outputs
- do not inflate historical artifacts into current authority
- do not suppress failing evidence
- keep changes scoped and reproducible
- path-portability fixes are welcome; hardcoded machine paths are not

## Recommended Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,netnew]"
```

## Minimum Contributor Checks

```bash
python -m pytest tests -q
make import-sanity
make portability-lint
```

## Evidence Discipline

- If your change affects claims, update the relevant proof docs.
- If your change finds a blocker, record the blocker. Do not narrate around it.
- Historical bundles under `proofs/artifacts/historical/` are preserved lineage,
  not editable current-authority targets.
