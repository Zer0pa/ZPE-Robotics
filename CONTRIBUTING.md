<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Contributing

Read this before opening a PR. The bar here is evidence, not intention.

<p>
  <img src=".github/assets/readme/section-bars/before-you-start.svg" alt="BEFORE YOU START" width="100%">
</p>

- Negative findings are first-class outputs.
- Do not inflate historical artifacts into current authority.
- Do not suppress failing evidence or mixed results.
- Keep changes scoped and reproducible.
- Do not upgrade docs into success language unless the governing proof files
  actually support it.
- Path-portability fixes are welcome. Hardcoded machine paths are not.

<p>
  <img src=".github/assets/readme/section-bars/environment-setup.svg" alt="ENVIRONMENT SETUP" width="100%">
</p>

Minimal contributor surface:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

If you are touching benchmark, telemetry, or dataset tooling:

```bash
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
```

<p>
  <img src=".github/assets/readme/section-bars/running-the-test-suite.svg" alt="RUNNING THE TEST SUITE" width="100%">
</p>

```bash
python -m pytest tests -q
python -m build
```

Add the narrower checks that match your change surface:

- CLI / packaging: `python -m pytest tests/test_release_surface.py tests/test_cli.py -q`
- workflow edits: `yamllint .github/workflows/*.yml`
- packet verification: `zpe-robotics verify proofs/release_candidate/canonical_release_packet.zpbot`

<p>
  <img src=".github/assets/readme/section-bars/what-we-accept.svg" alt="WHAT WE ACCEPT" width="100%">
</p>

- bug fixes with a reproducer and a clear non-regression path
- packaging or workflow corrections that make build, install, or release truth
  more accurate
- documentation corrections that tighten authority routing or remove stale claims
- additional falsification, adversarial, or comparator evidence
- path-portability cleanup that removes machine-specific assumptions

<p>
  <img src=".github/assets/readme/section-bars/what-we-do-not-accept.svg" alt="WHAT WE DO NOT ACCEPT" width="100%">
</p>

- changes that narrate engineering completion while `proofs/ENGINEERING_BLOCKERS.md`
  still governs
- claims of bit-exact replay, full Rust routing, or public-release readiness
  without proof
- PRs that remove or hide failing evidence
- hardcoded local paths or machine-specific shortcuts
- contract changes to the frozen packet surface without explicit evidence and
  review

<p>
  <img src=".github/assets/readme/section-bars/pr-process.svg" alt="PR PROCESS" width="100%">
</p>

1. Branch from `main` with one concern per branch.
2. Make the smallest coherent change that closes the issue you are working.
3. Run the relevant checks and keep the suite green.
4. Update proof docs or runbooks if your change affects claims, release paths,
   or support guidance.
5. Open the PR with exact commands, exact evidence paths, and any caveats.

<p>
  <img src=".github/assets/readme/section-bars/commit-style.svg" alt="COMMIT STYLE" width="100%">
</p>

- Use present tense and keep commits atomic.
- Prefer factual messages over narrative ones.
- If your change closes or documents a known blocker, say so directly.
