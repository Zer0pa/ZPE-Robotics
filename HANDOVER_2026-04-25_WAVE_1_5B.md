# ZPE-Robotics Wave 1.5b Handover

## Scope

This handover is for the current Wave 1.5b investor-readiness branch only.

- Canonical repo: `https://github.com/Zer0pa/ZPE-Robotics`
- Local working clone used in this session: `/Users/Zer0pa/ZPE/ZPE-Robotics-wave15b`
- Active branch: `chore/wave-1-5b-investor-readiness-2026-04-25`
- PR: `#20`
- PR URL: `https://github.com/Zer0pa/ZPE-Robotics/pull/20`

Do not assume this branch includes broader README or product-surface cleanup. That was attempted and then explicitly reverted to keep the branch narrow.

## Governing Intent

The final branch was reduced to the narrow, defensible CI/package-fix surface:

1. fix the failing `ruff` jobs on main
2. fix the `uv.lock` drift breaking `m1_ros2_probe`
3. harden `pyproject.toml` only within the already-touched metadata surface
4. avoid widening into README/product-claim surgery

## Current Branch Delta vs `origin/main`

Only these files differ from `origin/main`:

- `pyproject.toml`
- `tests/test_anomaly.py`
- `uv.lock`

Current diff summary from `git diff --stat origin/main...HEAD`:

```text
pyproject.toml        | 3 +--
tests/test_anomaly.py | 2 --
uv.lock               | 2 +-
3 files changed, 2 insertions(+), 5 deletions(-)
```

## Exact Changes on This Branch

### 1. `tests/test_anomaly.py`

Removed an unused `pytest` import.

Reason:

- `CI` / `ruff` failed on main
- `Test` / `ruff` failed on main
- exact failure was `F401` unused import in `tests/test_anomaly.py`

### 2. `pyproject.toml`

Two edits only:

- build backend range changed from:
  - `hatchling>=1.27`
  - to `hatchling>=1.27,<2`
- removed classifier:
  - `"License :: Other/Proprietary License"`

Reason:

- satisfy the Wave 1.5b pyproject hardening ask
- align with the existing PEP 639 cleanup already represented by open PR `#19`
- avoid touching version, license text, workflows, or unrelated metadata

### 3. `uv.lock`

Refreshed lockfile package identity from `zpe-motion-kernel` to `zpe-robotics`.

Reason:

- `m1_ros2_probe` on main failed at:
  - `uv sync --frozen --extra dev`
- exact failure:
  - lockfile still referenced missing workspace member `zpe-motion-kernel`

## What Was Tried and Then Reverted

There was an intermediate README narrowing pass in commit:

- `ec4d64a chore(robotics): harden investor-readiness surface`

That pass:

- deleted large parts of `README.md`
- removed public PyPI/package-public claims
- reframed the front door around only directly test-anchored runtime claims

That was later reverted by:

- `1a9a22f chore(robotics): revert readme narrowing`

Current branch HEAD:

- `1a9a22f`

Why it was reverted:

- user instruction: `fix and revert`
- safest interpretation was to revert the README narrowing while keeping the actual CI/package fixes
- final branch is now intentionally narrow

Do not reintroduce the README narrowing on this branch unless explicitly directed.

## PR State

- PR number: `20`
- title: `chore(robotics): Wave 1.5b investor-readiness hardening`
- base: `main`
- head: `chore/wave-1-5b-investor-readiness-2026-04-25`
- draft: `false`

PR body was updated after the README revert so it now describes the branch as:

- fixing the failing main CI/package issues
- reverting the README narrowing
- keeping scope narrow

## GitHub Checks State At Time of Handover

Passing checks observed on PR `#20`:

- `ruff` (CI)
- `ruff` (Test)
- `clean_clone_verify`
- `m1_ros2_probe`
- `pytest (ubuntu-latest, py3.11)`
- `pytest (ubuntu-latest, py3.12)`
- `pytest (arm64, py3.11)`
- `pytest x86 (py3.11)`
- `pytest x86 (py3.12)`
- `pytest macOS`
- `pytest ARM64`
- `Analyze (actions)`
- `Analyze (python)`
- `CodeQL`

Still queued at the last refresh:

- `pytest (macos-13, py3.11)` in `CI`
- `pytest (macos-13, py3.12)` in `CI`

Out-of-scope failing automation:

- `add-to-project`

Important:

- `add-to-project` is not part of the lane engineering fix surface
- do not distort the branch scope to chase that automation unless explicitly asked

## Local Verification Already Run

These were run successfully after the README revert:

```bash
/tmp/zpe-robotics-wave15b-verify/bin/python -m ruff check src tests
/tmp/zpe-robotics-wave15b-verify/bin/python -m pytest tests -q
/tmp/zpe-robotics-wave15b-verify/bin/python -m build
```

Results:

- `ruff`: pass
- `pytest`: `42 passed, 1 skipped`
- `python -m build`: pass

Additional verification already completed earlier in this branch:

```bash
/tmp/zpe-robotics-wave15b-tools/bin/uv lock
/tmp/zpe-robotics-wave15b-tools/bin/uv sync --frozen --extra dev
```

These were used specifically to validate the lockfile fix.

## Temp Tooling Created During This Session

These temporary environments were used:

- `/tmp/zpe-robotics-wave15b-tools`
- `/tmp/zpe-robotics-wave15b-verify`

They are not part of the repo.

## Known Environment Quirk

Every shell command emitted:

```text
/Users/prinivenpillay/.zshenv:.:4: no such file or directory: /Users/Zer0pa/ZPE/.codex-zpe-env.zsh
```

This was noisy but non-blocking in this session.

Do not mistake it for the repo issue being fixed here.

## Mainline Failure Analysis That Led to the Current Fix

Before changes, current `main` failures were:

1. `CI` / `ruff`
2. `Test` / `ruff`
3. `M1 ROS2 Probe`

Root causes:

1. `ruff`:
   - unused `pytest` import in `tests/test_anomaly.py`

2. `m1_ros2_probe`:
   - stale `uv.lock`
   - missing workspace member/package identity mismatch

These were the actual branch targets. No broader source refactor was needed.

## Other Repo Context Observed During This Session

Relevant but not changed in the final branch:

- open PR `#19` exists for the PEP 639 classifier fix
- the branch incorporated the same classifier removal directly into this Wave 1.5b branch
- `README.md` on `main` still contains broader product/marketing/public-package claims
- those claims were not settled in the final branch because the README narrowing was reverted

Important for future work:

- if a later agent is asked to do README/proof/test anchoring properly, that should likely happen as a separate scoped pass, not by stealth inside this branch

## Exact Git History Relevant to This Branch

Recent commits:

```text
1a9a22f chore(robotics): revert readme narrowing
ec4d64a chore(robotics): harden investor-readiness surface
3354e36 harden Robotics metadata and reconcile attack 5 (#18)
```

Interpretation:

- `ec4d64a` introduced the CI/package fixes and also the README narrowing
- `1a9a22f` reverted the README narrowing only
- current branch result is the intended narrow delta

## If a New Agent Needs to Resume Immediately

Use this sequence:

```bash
cd /Users/Zer0pa/ZPE/ZPE-Robotics-wave15b
git fetch origin
git checkout chore/wave-1-5b-investor-readiness-2026-04-25
git status --short --branch
gh pr view 20 --repo Zer0pa/ZPE-Robotics
gh pr checks 20 --repo Zer0pa/ZPE-Robotics
git diff --stat origin/main...HEAD
```

If local verification needs to be rerun:

```bash
/tmp/zpe-robotics-wave15b-verify/bin/python -m ruff check src tests
/tmp/zpe-robotics-wave15b-verify/bin/python -m pytest tests -q
/tmp/zpe-robotics-wave15b-verify/bin/python -m build
```

If the temp venv no longer exists:

```bash
python3 -m venv /tmp/zpe-robotics-wave15b-verify
/tmp/zpe-robotics-wave15b-verify/bin/pip install -e '.[dev]' build
```

## What the Next Agent Should Not Redo

Do not:

- re-triage the main failure root causes from scratch
- reopen README narrowing unless explicitly asked
- touch `.github/workflows/` to chase `add-to-project`
- bump version
- edit `LICENSE`, `CITATION.cff`, `.zenodo.json`, `SECURITY.md`, or `REPRODUCIBILITY.md`
- broaden this branch into feature or product-claim work

## What the Next Agent Should Check First

1. whether the two queued CI macOS jobs have finally completed
2. whether PR `#20` has new review comments
3. whether PR `#19` is still open or has merged, to avoid duplicated metadata churn across branches

## Practical Next Actions Depending on State

### If the queued CI macOS jobs pass

- leave the code surface alone
- update PR body only if it still says those jobs are pending
- wait for review or address review comments only

### If one of the queued CI macOS jobs fails

- inspect that exact job log first
- compare against the already-passing `pytest macOS` job in the `Test` workflow
- keep the fix narrow and avoid reopening README work

### If a reviewer asks for broader README cleanup

- treat that as new scope
- do not assume it belongs in this PR without explicit instruction

## Bottom Line

At handover time, the branch is stable and narrow:

- the real failing main jobs were fixed
- the README narrowing was reverted
- the branch delta against `main` is only `pyproject.toml`, `tests/test_anomaly.py`, and `uv.lock`
- PR `#20` is the live coordination point

