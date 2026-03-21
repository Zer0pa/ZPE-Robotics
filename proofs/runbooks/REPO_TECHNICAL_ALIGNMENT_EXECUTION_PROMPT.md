# REPO_TECHNICAL_ALIGNMENT_EXECUTION_PROMPT

Date: 2026-03-21
Owner: Git Orchestrator
Use: give this to a repo-specific agent when you want it to inspect, plan, execute, verify, and report technical release-architecture work end to end

You are doing technical release-architecture execution for one repo in the ZPE family.

Read these first and follow them:

1. `/Users/Zer0pa/ZPE/Git Orchestreator/AGENT_RULES.md`
2. `/Users/Zer0pa/ZPE/Git Orchestreator/WORK_RECEIPT_TEMPLATE.md`

Core instruction:

- do not stop at analysis
- do not stop at recommendations
- inspect the repo
- determine the truthful target architecture
- make the technical changes
- verify them
- write the receipt
- report only when the technical execution pass is complete or a real blocker exists

Scope:

This is a technical coding and engineering task.

Stay focused on:
- package structure
- build system
- install path
- dependency declarations
- optional extras
- native build integration
- CLI entry points
- release workflow
- trusted publishing path
- runtime/import surface
- test and verification path
- artifact and packaging truth

Do not spend your time on:
- marketing copy
- product messaging
- README polish
- public-facing success language
- broad repo reorganization
- governance prose
- presentation cleanup

Allowed doc changes are only the minimum technical surfaces required to make the build, install, release, or verification path truthful and usable, such as:
- `pyproject.toml`
- `Cargo.toml`
- package metadata
- release workflow files
- install/runbook files that are part of the technical release path

Do not invent IMC runtime coupling.

Treat `ZPE-IMC` as:
- a benchmark/reference line
- a source of static contract ideas where explicitly relevant
- not a default runtime dependency

If shared family coupling is needed, prefer one of these in order:

1. no coupling
2. shared static contract artifact
3. tiny extracted shared package
4. full runtime dependency only if the repo truly already needs it

You must determine which of these the current repo really is:

- standalone package
- standalone package plus native helper
- multi-runtime codec repo
- app/service repo
- not a truthful public distribution surface yet

Then you must execute the repo toward its truthful next technical state.

Execution requirements:

- inspect current packaging, imports, workflows, and release surfaces
- identify contradictions between package truth and repo truth
- identify undeclared dependencies, broken extras, misleading CLI/package names, native-build drift, and release-workflow gaps
- choose the minimum technically correct target architecture
- implement the technical fixes now
- keep changes bounded and coherent
- do not rewrite the whole repo unless required
- do not touch unrelated work

Specific goals:

- make install surfaces truthful
- make dependency declarations truthful
- make native build behavior truthful
- make CLI entry points truthful
- make release workflows truthful
- make test and verification entry points truthful
- leave product/public docs frozen unless a technical release path would otherwise be false

Verification requirements:

- build the package or packages
- run the relevant tests
- verify import/install behavior
- verify release workflow logic statically if it cannot be run live
- verify that the resulting repo state matches the chosen architecture

If the repo is not ready for public release, do not fake readiness.
Instead, still complete the technical alignment pass and leave it in the best truthful engineering state.

Your final report must contain:

1. classification
2. target architecture chosen
3. technical changes made
4. verification performed
5. remaining real blockers only
6. whether the repo is now technically ready for final documentation and release-surface finalization

If you finish the technical pass and the repo is ready for the next non-technical step, say exactly:

`This repo is technically aligned for final release-surface documentation and finalization.`

If not, say exactly what technical gap remains and why it is still open.

Before finishing, write one repo-local receipt using:

`/Users/Zer0pa/ZPE/Git Orchestreator/WORK_RECEIPT_TEMPLATE.md`

Do the full job.
Do not stop halfway.
Do not narrate success beyond the proof surface.
