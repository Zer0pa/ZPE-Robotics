# REPO_TECHNICAL_EXECUTION_SUPPLEMENT

Date: 2026-03-21
Owner: Git Orchestrator
Use: repo-specific engineering guidance to be used together with
`REPO_TECHNICAL_ALIGNMENT_EXECUTION_PROMPT.md` and
`UNIVERSAL_REPO_TECHNICAL_EXECUTION_DISPATCH_PROMPT.md`

This file is a supplement, not a replacement.

Use the universal execution prompt first.
Then apply the section that matches the repo you are working in.

## Family Rule

- Do not force runtime coupling to `ZPE-IMC`.
- Treat `ZPE-IMC` as a benchmark/reference line and a source of static contract
  ideas unless the repo truly already needs IMC code in runtime.
- Prefer this order:
  1. no coupling
  2. shared static contract artifact
  3. tiny extracted shared package
  4. full runtime dependency only if the repo truly needs it

## Coverage Index

Use these bindings when deciding which section applies:

- `ZPE Ink -> /Users/Zer0pa/ZPE/ZPE Ink/ZPE-Ink`
- `ZPE FT -> /Users/Zer0pa/ZPE/ZPE FT/zpe-finance`
- `ZPE Geo -> /Users/Zer0pa/ZPE/ZPE Geo/zpe-geo`
- `ZPE Mocap -> /Users/Zer0pa/ZPE/ZPE Mocap/ZPE-Mocap`
- `ZPE Neuro -> /Users/Zer0pa/ZPE/ZPE Neuro/ZPE-Neuro`
- `ZPE Robotics -> /Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`
- `ZPE Robotics-GPD -> /Users/Zer0pa/ZPE/ZPE Robotics`
- `ZPE Video -> /Users/Zer0pa/ZPE/ZPE Video/zpe-video`
- `ZPE Prosody -> /Users/Zer0pa/ZPE/ZPE Prosody/ZPE-Prosody`
- `ZPE XR -> /Users/Zer0pa/ZPE/ZPE XR/ZPE-XR`
- `Bio / Bio Wearable -> /Users/Zer0pa/ZPE/ZPE Bio/zpe-bio`
- `ZPE IoT -> /Users/Zer0pa/ZPE/ZPE IoT/zpe-iot`
- `IMC -> /Users/Zer0pa/ZPE-IMC-REPO`
- `Zer0paShip -> /Users/Zer0pa/Zer0paShip`
- `Tokenizer -> no authoritative local git repo currently`
- `Test -> no authoritative local git repo currently`

## Robotics

If you are in `ZPE-Robotics`:

- treat the truthful current public wedge as the package, not the whole
  robotics stack
- do not claim full robotics-platform readiness if the repo only supports a
  narrower kernel surface
- resolve naming truth across:
  - repo name
  - distribution name
  - import package name
  - CLI name
- fix undeclared extras and runtime dependencies
- fix trusted-publishing and release-surface truth
- if Rust or native code is the technically correct path, do not avoid it
- do not accept a weaker Python-only shortcut unless it is actually the better
  engineering choice
- treat the current release-candidate wedge as a repo-root Python package
  (`zpe-motion-kernel`) with external ROS2/MoveIt2 and `mcap` probe paths, not
  a shipped native-helper repo
- keep latent PyPI trusted-publishing surfaces from implying public release;
  publication is still a separate gate decision
- treat Comet and Opik telemetry as optional sidecars; if package code imports
  them, declare them as extras rather than implicit runtime deps
- keep IMC linkage static and documentary unless a real shared runtime contract
  is deliberately introduced

## Bio / Bio Wearable

If you are in `ZPE-Bio`:

- treat it as a standalone package with sibling Rust and embedded surfaces
- do not blur the Python package, Rust codec, and embedded target into one
  fake release unit
- make packaging boundaries explicit
- make versioning coherent across Python and native surfaces if they are meant
  to move together
- do not rely on ignored validation results as if they are part of the tracked
  release surface
- ensure optional extras and local dataset requirements are truthful

## FT

If you are in `ZPE-FT`:

- treat it as a standalone Python package with an optional repo-local native
  helper
- do not pretend the native helper is packaged if the release path does not
  actually build and publish it
- either integrate native build truthfully or make the Python fallback the
  explicit supported path
- remove repo-local `PYTHONPATH` assumptions from the claimed install path
- make observability dependencies truthful, including optional ones

## Geo

If you are in `ZPE-Geo`:

- treat it as a standalone package candidate, not a live public artifact yet
- eliminate repo-layout assumptions from packaged runtime behavior where
  possible
- make fallback behavior explicit and technically honest
- do not allow a default install to silently diverge from the adjudicated
  evidence path

## Ink

If you are in `ZPE-Ink`:

- treat it as a standalone codec repo with multiple runtime bindings
- do not let Python, Rust, WASM, Swift, and C# bindings drift apart silently
- prefer a single source of truth for the packet contract if the current design
  duplicates it too widely
- do not treat cross-runtime parity ambitions as solved if the release gate is
  still externally blocked

## IoT

If you are in `ZPE-IoT`:

- treat it as a private-stage multi-surface codec repo: Python package plus
  CLI, sibling Rust core crate, non-published PyO3 bridge, and C/embedded
  surface
- do not blur `python/`, `core/`, `python/native/`, and `c/` into one release
  unit
- keep IMC linkage at `docs/family/` contract level only; do not add IMC
  runtime imports
- keep chemosense local smoke or CLI metrics local; family coordination
  authority stays the pinned IMC compatibility vector

## Mocap

If you are in `ZPE-Mocap`:

- treat the repo root as a proof/docs shell with the installable Python package
  nested under `code/`
- treat the truthful current wedge as the deterministic Python
  codec/search/reference package, not a full DCC integration stack
- do not promote Blender, BVHIO, or USD compatibility beyond the current
  simulated notes
- audit inherited IMC metadata, links, and optional extras before release;
  Mocap package metadata must describe Mocap itself
- do not assume CI or release automation exists just because the repo has
  `.github/`; current workflow is project-board automation only

## Neuro

If you are in `ZPE-Neuro`:

- treat it as a standalone Python package with a script-driven gate harness and
  bounded public-corpus replay surfaces
- keep the default package install separate from heavy proof and replay extras;
  declare replay dependencies truthfully and do not imply clean-clone replay
  from the base install
- keep synthetic Wave-1 gates, DANDI/AJILE evaluation, and IBL chunked probes
  as distinct documented surfaces
- do not add IMC runtime coupling or family-contract docs unless a real
  downstream contract exists

## Prosody

If you are in `ZPE-Prosody`:

- treat it as a standalone Python package with an optional API/service wrapper,
  not as a service-first repo
- keep the zero-dependency core package separate from heavy Gate-M resource
  scripts and external-corpus tooling
- allow narrow `docs/family/` artifacts only as static release-contract
  metadata when runtime coupling is explicitly none
- do not treat in-process API-contract validation as proof that the
  FastAPI/Uvicorn deployment surface is already closed

## Video

If you are in `ZPE-Video`:

- treat it as a private staging benchmark harness with a small package core,
  not as a truthful public distribution surface yet
- separate the zero-dependency package claim from gate paths that require
  `.env`, `docs/inputs/*`, dataset trees, `ffmpeg`, and detector/measurement
  stacks
- keep authoritative execution in `scripts/execute_wave1.py` and
  `Wave1Pipeline`; do not imply a clean installed CLI or service surface
- do not add IMC family docs or phantom `requirements.txt`; fix local package
  and gate truth first

## XR

If you are in `ZPE-XR`:

- treat it as a private-stage Python package candidate with a repo-local Rust
  extension and staged verification harness
- make one Python source root canonical; do not let `code/source/zpe_xr` and
  `code/src/zpe_xr` drift silently
- keep `executable/verify.py` path-probing behavior out of the claimed
  installed runtime surface
- do not promote package-candidate packaging into runtime closure, photon
  displacement, exact-corpus closure, or public-release readiness

## IMC (ZPE-IMC-REPO)

If you are in `ZPE-IMC`:

- preserve its role as the authoritative multimodal integration repo and family
  benchmark/reference line; do not turn it into the default runtime base for
  sibling lanes
- treat the repo as multi-surface: repo-root docs/proofs, Python package in
  `code/`, Rust native extension in `code/rust/imc_kernel`, private WASM parity
  package in `code/wasm`, and operator rerun harness in `executable/`
- do not treat repo root as the pip package; the Python distribution and CLI
  live under `code/`
- keep family reuse on static contract artifacts
  (`docs/family/IMC_INTERFACE_CONTRACT.md`,
  `docs/family/IMC_COMPATIBILITY_VECTOR.json`), not runtime imports
- distinguish release-upload truth from operator-authority truth: the release
  workflow uploads `code/dist/*`, while the accepted runtime authority path
  requires the Rust extension and `executable/run_with_comet.py`
- do not promote sibling Rust or WASM surfaces with `publish = false` or
  `private: true` into public release promises

## Zer0paShip

If you are in `Zer0paShip`:

- treat it as a ship-design execution workspace with repo-local Python
  modules, not as a package-first public distribution surface
- obey runbook and phase authority before implementation; `runbooks/` and
  `docs/PHASE.md` outrank generic repo-cleanup instincts
- keep RunPod and output-path contracts truthful, especially
  `/workspace/Zer0pa_Freighter`, `output/ship/`, `output/platform/`, and
  `output/systems/`
- do not let packaging polish, app/service framing, or proxy metrics outrank
  the governing vessel acceptance gate

## Robotics-GPD

If you are in `ZPE-Robotics-GPD`:

- treat it as an orchestration and research lane, not the public product
  package surface
- do not solve product packaging by editing this repo if the authoritative
  product runtime lives in `zpe-robotics`
- keep its role narrow: planning, phase control, research execution, and
  handoff into the real product repo

## Tokenizer Workspace (Control-Lock Only)

If you are working on the Tokenizer control plane:

- treat it as a governed workspace, not an authoritative local git repo
- current local path is `/Users/Zer0pa/ZPE/ZPE Tokenizer`
- no authoritative local `.git` repo exists there right now
- do not dispatch repo-technical execution work as if this were a cloned repo
- if dossier references are needed, use the actual local file names rather than
  doctrine aliases until the surface is corrected

## External Auditor Snapshot (ZPE-Test)

If you are dealing with `ZPE-Test`:

- treat it as an external-only acquisition surface until it is actually cloned
  locally
- no authoritative local repo exists under `/Users/Zer0pa` right now
- do not write local repo-alignment tasks against it until there is a real
  local clone

## Other Lanes

If you are in a repo not explicitly listed above:

- begin by classifying it honestly:
  - standalone package
  - standalone package plus native helper
  - multi-runtime codec repo
  - app/service repo
  - not a truthful public distribution surface yet
- do not assume standalone if the repo clearly has nested code, native, or
  multi-runtime surfaces
- do not add IMC runtime dependency by default
- fix package truth before chasing family-level coupling
- if a local static contract exists, treat that as the likely family linkage
  surface

## Escalation Rule

If, after inspection, you discover that the repo truly shares runtime code with
another lane and duplication is now materially harmful, do not silently invent
cross-repo imports.

Instead:
- complete the local technical pass first
- document the exact duplicated surface
- recommend a tiny extracted shared package as a follow-on
- leave a receipt with concrete file paths and rationale
