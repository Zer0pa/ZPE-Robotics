# Zer0pa Repo Docs Playbook

## Purpose
This playbook is the shareable operating standard for Zer0pa repository documentation work.

It uses ZPE-IMC as the canonical example, but it is written for reuse across derivative repos such as ZPE-FT, ZPE-Bio, ZPE-IoT, and other related workstreams.

The objective is simple:
- make each repo honest about its own current truth
- keep the documentation surface coherent and GitHub-safe
- preserve the ZPE-IMC visual system while a derivative repo is still bootstrapping
- use agents and subagents where they help, without turning the process into theater

## Current Authority Baseline
For current repo-shape truth, treat this repo as the authority example:
- canonical working repo: `/Users/Zer0pa/ZPE-IMC-REPO`
- current live public repo: `https://github.com/Zer0pa/ZPE-IMC` on `main`

Use both layers deliberately:
- local working repo is edit authority
- live public repo is public-render authority
- if they diverge, do not hand a derivative repo a guessed standard; reconcile first

For historical operations memory and prior wave evidence, use:
- legacy ops/evidence root: `/Users/Zer0pa/ZPE/ZPE-IMC/agent_ops`

Current counted canonical registry basis:
- `/Users/Zer0pa/ZPE-IMC-REPO/agent_ops/repo_augmentation_wave_20/artifacts/WP_B/CANONICAL_DOC_SET_POST.tsv`

Current registry count:
- `27` counted canonical docs

Important distinction:
- The `27`-file registry is the counted canonical public/governance set.
- A small number of additional supporting authority files are still operationally mandatory even though they were outside that counted registry.
- Do not confuse counted-registry scope with total documentation authority.

## Non-Negotiable Repo Docs Rules
1. Every repo must document its own truth, not inherit ZPE-IMC claims.
2. A derivative repo may inherit the ZPE-IMC doc structure, tables, GIF system, nav system, and section-bar system, but not ZPE-IMC metrics, statuses, or proof claims.
3. If a claim is not evidenced in that repo, mark it `UNKNOWN`, `UNVERIFIED`, `INFERRED`, owner-deferred, or remove it.
4. Keep canonical anchors stable per repo. For ZPE-IMC these are:
   - `https://github.com/zer0pa/zpe-imc`
   - `architects@zer0pa.ai`
5. Keep forbidden public regressions out unless explicitly re-authorized.
   - In ZPE-IMC this included `arxiv` and `dossier` regressions.
6. Keep GIFs and section-bar rendering reliable. Broken asset paths are documentation failures.
7. Use tables where the reader needs comparison, status, scope, counts, boundaries, or evidence paths.
8. No speculative capability inflation. Boundaries and gaps are part of the product truth.

## Visual System That Derivative Repos Should Initially Reuse
Until a derivative repo is ready for its own custom media pass, copy the ZPE-IMC visual system exactly.

Shared masthead asset used across docs:
- `/Users/Zer0pa/ZPE-IMC-REPO/.github/assets/readme/zpe-masthead.gif`

Root README-only additional GIFs:
- `/Users/Zer0pa/ZPE-IMC-REPO/.github/assets/readme/zpe-masthead-option-3-2.gif`
- `/Users/Zer0pa/ZPE-IMC-REPO/.github/assets/readme/zpe-masthead-option-3-3.gif`

Other current README assets worth retaining during bootstrap:
- nav buttons: `/Users/Zer0pa/ZPE-IMC-REPO/.github/assets/readme/nav/`
- section bars: `/Users/Zer0pa/ZPE-IMC-REPO/.github/assets/readme/section-bars/`
- license callout: `/Users/Zer0pa/ZPE-IMC-REPO/.github/assets/readme/callouts/license-free-tier-reverse.svg`

Render rules:
- Root README keeps three animated GIF placements.
- Other docs keep the shared masthead only unless there is a strong reason otherwise.
- Section bars remain black with white uppercase labels.
- Use GitHub-safe Markdown + safe HTML only.
- Relative paths must match document depth.
  - root docs: `.github/assets/readme/...`
  - `docs/*.md`: `../.github/assets/readme/...`
  - `docs/family/*.md` and `code/README.md`: `../../.github/assets/readme/...`

## Current Live Quality Lessons From ZPE-IMC
These are not abstract preferences. They come from the current public repo surface and from the fixes required to get there.

1. The root README works best when it is dense but not bloated.
- The current live public README is materially more concise than the larger working copy that existed during intermediate waves.
- Treat the live front door as the shape authority for README density and scan speed.

2. Promote a fact once, then route.
- A promoted run identity, throughput set, or authority block should appear once in its canonical location.
- Later sections should point back to it instead of duplicating the same values in new card rows or duplicate tables.

3. Supporting docs should carry depth, not duplicate the front door.
- `README.md` should summarize and route.
- `docs/ARCHITECTURE.md` should map where truth lives.
- `AUDITOR_PLAYBOOK.md` should give the shortest honest replay path.
- `PUBLIC_AUDIT_LIMITS.md` should state what cannot be inferred.
- `docs/FAQ.md` should answer likely reader objections and conceptual questions.

4. Tables matter when they integrate information.
- The strongest ZPE-IMC docs use tables to combine status, scope, evidence, and boundaries in one place.
- Decorative tables or repeated metric tables are noise.

5. Public rendering is part of quality.
- A doc is not done just because the Markdown file looks reasonable locally.
- The GitHub-rendered surface, asset visibility, and scan order are part of the acceptance gate.

## Canonical Document Surface For ZPE-IMC

### A. Counted canonical public/governance registry (`27`)
These are the files currently counted in the post-Wave-20 canonical registry.

| Path | Role | How it differs | Interrelates with |
|---|---|---|---|
| `/Users/Zer0pa/ZPE-IMC-REPO/README.md` | Front door. Product story, current authority, modality snapshot, throughput, proof routing, next steps. | Only file that carries the full narrative stack and all three GIFs. | `AUDITOR_PLAYBOOK.md`, `PUBLIC_AUDIT_LIMITS.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`, proof anchors. |
| `/Users/Zer0pa/ZPE-IMC-REPO/CHANGELOG.md` | Public release-surface delta log. | Change history, not architecture or audit instruction. | `README.md`, `RELEASING.md`, `LICENSE`, `docs/LEGAL_BOUNDARIES.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/CITATION.cff` | Citation metadata for the repo/software record. | Machine-readable citation surface, not narrative prose. | `README.md`, `LICENSE`, external repo metadata. |
| `/Users/Zer0pa/ZPE-IMC-REPO/CODE_OF_CONDUCT.md` | Community behavior standard. | Social conduct contract, not technical contribution policy. | `CONTRIBUTING.md`, GitHub templates. |
| `/Users/Zer0pa/ZPE-IMC-REPO/CONTRIBUTING.md` | Contribution entry rules and evidence discipline. | Tells contributors how to work; does not define project architecture. | `CODE_OF_CONDUCT.md`, PR template, issue templates, `README.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/GOVERNANCE.md` | Public governance boundary for evidence, claims, status semantics, compatibility posture. | Policy/decision surface, not release log or implementation guide. | `README.md`, `ROADMAP.md`, `RELEASING.md`, `PUBLIC_AUDIT_LIMITS.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/LICENSE` | Legal source of truth. | Only authoritative legal text. Everything else must defer to it. | `CITATION.cff`, `docs/LEGAL_BOUNDARIES.md`, package metadata. |
| `/Users/Zer0pa/ZPE-IMC-REPO/ROADMAP.md` | Status-first planning and downstream posture. | Future-facing posture document, not a guarantee ledger. | `GOVERNANCE.md`, `RELEASING.md`, `README.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/SECURITY.md` | Vulnerability reporting and support boundary for security issues. | Security operations surface, not general support or bug triage. | GitHub issue templates, `README.md`, `CONTRIBUTING.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/ARCHITECTURE.md` | Canonical architecture index and runtime authority map. | Explains where truth lives and how runtime/build/proof layers fit together. | `README.md`, `docs/family/IMC_INTERFACE_CONTRACT.md`, proof logs. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/FAQ.md` | Public Q&A for outsiders. | Reader-assistance surface, not the governing truth by itself. | `README.md`, `AUDITOR_PLAYBOOK.md`, `PUBLIC_AUDIT_LIMITS.md`, `SECURITY.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/README.md` | Documentation index and routing layer. | Directory map, not front-door persuasion. | `docs/FAQ.md`, `docs/SUPPORT.md`, family docs, proof corpus. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SUPPORT.md` | Support routing and response expectations. | Operational contact/routing surface, not contribution policy. | `README.md`, `docs/FAQ.md`, `SECURITY.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/.github/PULL_REQUEST_TEMPLATE.md` | PR intake discipline. | GitHub workflow artifact, not public explanatory prose. | `CONTRIBUTING.md`, `GOVERNANCE.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/.github/ISSUE_TEMPLATE/bug_report.md` | Bug intake structure. | Focused on reproducible defects. | `SECURITY.md`, `CONTRIBUTING.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/.github/ISSUE_TEMPLATE/evidence_dispute.md` | Claims/evidence dispute intake. | Handles disagreement over proof/claims rather than code defects. | `GOVERNANCE.md`, `PUBLIC_AUDIT_LIMITS.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/.github/ISSUE_TEMPLATE/feature_request.md` | Feature intake structure. | Product/request routing, not claims verification. | `ROADMAP.md`, `CONTRIBUTING.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/.github/ISSUE_TEMPLATE/question.md` | Question intake structure. | General Q&A intake. | `docs/FAQ.md`, `docs/SUPPORT.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/Zer0pa SAL 6.2/Zer0pa_SAL_v6_2_FINAL_deterministic.docx` | Canonical retained SAL source artifact. | Source-pack artifact, not a rendered repo-policy doc. | `LICENSE`, SAL governance markdown set. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/Zer0pa SAL 6.2/Zer0pa_SAL_v6_2_FINAL_deterministic.txt` | Canonical retained SAL text artifact. | Plain-text legal source artifact, not repo-facing summary prose. | `LICENSE`, SAL governance markdown set. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/EQUIVALENCE_DISPUTE_WORKFLOW.md` | Governance procedure for equivalence disputes. | Specialized legal/governance workflow, not core repo onboarding. | `GOVERNANCE.md`, `LICENSE`, `LEGAL_MESSAGE_CONTROL_PACK.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/FUNCTIONAL_EQUIVALENCE_TEST_STANDARD.md` | Standard for assessing functional equivalence. | Evaluation standard, not repo build/runtime guidance. | `EQUIVALENCE_DISPUTE_WORKFLOW.md`, `INDEPENDENT_DEVELOPMENT_STANDARD.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/INDEPENDENT_DEVELOPMENT_STANDARD.md` | Standard for independent-development posture. | Governance/legal standard, not engineering contribution rules. | `FUNCTIONAL_EQUIVALENCE_TEST_STANDARD.md`, `PRIOR_ART_POSITIONING_GUARDRAILS.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/LEGAL_MESSAGE_CONTROL_PACK.md` | Controlled public/legal messaging guardrails. | Messaging discipline, not technical architecture. | `GOVERNANCE.md`, `PRIOR_ART_POSITIONING_GUARDRAILS.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/PRIOR_ART_POSITIONING_GUARDRAILS.md` | Prior-art/public-positioning constraints. | Positioning/legal boundary surface, not product FAQ. | `CITATION.cff`, `LEGAL_MESSAGE_CONTROL_PACK.md`, `GOVERNANCE.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/REVENUE_THRESHOLD_TRANSITION_POLICY.md` | Revenue-threshold transition policy. | Commercial/governance threshold rule, not license body. | `LICENSE`, `README.md`, `docs/LEGAL_BOUNDARIES.md`. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/SAL Governance Docs/TERMINATION_ENFORCEMENT_PROTOCOL.md` | Enforcement/termination procedure. | Governance protocol, not contributor workflow. | `LICENSE`, `GOVERNANCE.md`, `LEGAL_MESSAGE_CONTROL_PACK.md`. |

### B. Supporting authority docs that are not optional in practice
These files were not part of the counted `27`, but they are operationally important and should be treated as active supporting authority.

| Path | Role | Why it matters |
|---|---|---|
| `/Users/Zer0pa/ZPE-IMC-REPO/AUDITOR_PLAYBOOK.md` | Shortest honest outsider audit path. | This is the fastest way for an external reviewer to verify the repo without reading everything. |
| `/Users/Zer0pa/ZPE-IMC-REPO/PUBLIC_AUDIT_LIMITS.md` | Honesty boundary for what public audit can and cannot prove. | Prevents overstating what a public snapshot establishes. |
| `/Users/Zer0pa/ZPE-IMC-REPO/code/README.md` | Package-facing install/runtime/API surface. | Needed because repo-root README should not carry all package details. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/LEGAL_BOUNDARIES.md` | Compact release-surface legal boundary note. | Keeps smell/taste/package/legal caveats close to the public docs without overloading the license body. |
| `/Users/Zer0pa/ZPE-IMC-REPO/RELEASING.md` | Public release gate and decision boundary. | Critical for release semantics even though it fell outside the counted `27` registry. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/family/IMC_INTERFACE_CONTRACT.md` | Frozen downstream contract. | This is the machine/human contract for downstream integrations. It is canonical even if it sat outside a prior registry count. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/family/IMC_RELEASE_NOTE_FOR_BIO_IOT.md` | Family-facing downstream handoff note. | Needed for downstream consumers and release coordination. |
| `/Users/Zer0pa/ZPE-IMC-REPO/docs/family/IMC_COMPATIBILITY_VECTOR.json` | Machine-readable compatibility anchor. | Not Markdown, but still canonical. Downstream alignment depends on it. |

## How These Documents Interrelate
Think of the ZPE-IMC docs as six layers.

1. Front door
- `README.md`
- This tells the story, sets the current authority frame, and routes readers onward.

2. Reader support
- `docs/README.md`
- `docs/FAQ.md`
- `docs/SUPPORT.md`
- `AUDITOR_PLAYBOOK.md`
- `PUBLIC_AUDIT_LIMITS.md`
- These help outsiders and reviewers navigate without guessing.

3. Engineering/runtime truth mapping
- `docs/ARCHITECTURE.md`
- `code/README.md`
- `docs/family/IMC_INTERFACE_CONTRACT.md`
- `docs/family/IMC_COMPATIBILITY_VECTOR.json`
- These explain how the accepted path actually works and where runtime or contract truth lives.

4. Governance and release boundary
- `GOVERNANCE.md`
- `RELEASING.md`
- `ROADMAP.md`
- `SECURITY.md`
- `docs/LEGAL_BOUNDARIES.md`
- These define what can be said, what can be shipped, what remains gated, and how external issues are routed.

5. Community and intake
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- issue templates
- These turn policy into repeatable contributor behavior.

6. Citation and legal custody
- `LICENSE`
- `CITATION.cff`
- `docs/SAL Governance Docs/*`
- These define legal terms, citation posture, and governance around equivalence/prior-art/commercial thresholds.

## Cross-Document Coherence Locks
Before calling a repo doc surface good, check that these tokens are coherent across the relevant files.

1. Acquisition surface
- `README.md`
- `AUDITOR_PLAYBOOK.md`
- `docs/ARCHITECTURE.md`
- `SECURITY.md` if it names the public snapshot

2. Canonical repo URL and contact
- `README.md`
- `GOVERNANCE.md`
- `RELEASING.md`
- `SECURITY.md`
- `CITATION.cff`

3. License identity
- `LICENSE`
- `README.md`
- `CITATION.cff`
- `docs/LEGAL_BOUNDARIES.md`
- package metadata if exposed publicly

4. Promoted authority metrics and run IDs
- `README.md`
- `AUDITOR_PLAYBOOK.md`
- `PUBLIC_AUDIT_LIMITS.md`
- `code/README.md`
- `docs/ARCHITECTURE.md`

5. Public-truth versus operator/local-truth split
- `README.md`
- `AUDITOR_PLAYBOOK.md`
- `PUBLIC_AUDIT_LIMITS.md`

Rule:
- if one doc intentionally differs from another, the reason must be explicit
- silent drift is failure

ZPE-IMC lesson:
- local working docs and live public docs did diverge during the process
- future repos should assume this can happen and run a coherence pass before templating from any one surface

## What Worked In ZPE-IMC Quality Management
These parts worked and should be kept.

1. Truth-first edits
- The documentation improved most when claims were tied back to proof paths, runtime artifacts, or explicit caveats.

2. Tables for hard facts
- Status, metrics, compatibility, and scope boundaries became much clearer when they were turned into tables instead of long prose.

3. Separate surfaces for separate audiences
- README for the front door.
- Architecture for technical structure.
- Auditor playbook for outsiders.
- Governance/legal docs for boundary conditions.
- GitHub templates for intake discipline.

4. Explicit distinction between current truth and historical anchors
- ZPE-IMC only became legible once compatibility anchors, public-audit truth, and current operator truth were separated.

5. Falsification as a real gate
- The best documentation changes were the ones that survived an adversarial pass checking path integrity, claim drift, and public honesty.

6. Concision through de-duplication
- The public surface improved when repeated authority cards and repeated metric tables were collapsed into a single stronger authority block.
- Shorter was better only when nothing important was lost.

## What Hurt And Should Be Removed
This is the part to copy forward carefully.

1. Too many roles touching the same file
- Copy, layout, augmentation, art direction, and closeout layers repeatedly collided when multiple agents touched the same README/doc body.

2. Artifact and process theater
- Large wave packs, placeholder files, and ceremonial status docs created the appearance of rigor while sometimes obscuring the real state.

3. Registry drift
- Old counted sets remained in circulation after the live repo shape changed.
- Result: agents worked off stale inventories.

4. Local vs remote confusion
- Review repos, test repos, and working repos drifted unless one lane and one source of truth were enforced.

5. Design work done before truth discipline
- When design moved ahead of claim hygiene, good-looking documents still carried bad or mixed authority signals.

## Lean Operating Model For Future Repo Docs Work
Do not default to a five-agent theater chain.

Use this instead.

### Default model
1. Lead docs owner
- Owns the real file edits.
- Owns the final integration.
- No one else edits the same file concurrently.

2. Optional evidence extractor
- Read-only.
- Builds a short claim/evidence map or scans proof locations.
- Good subagent candidate.

3. Optional design implementer
- Only if layout or rendering work is actually needed.
- Must not rewrite claims.
- Good subagent candidate when write scope is disjoint, for example SVG/nav assets only.

4. Falsifier
- Checks anchors, drift, rendering paths, unsupported claims, and scope discipline.
- Read-only unless the brief explicitly authorizes mechanical repair.

### Do not add these roles unless there is a real reason
- separate copy augmentor
- separate art direction refiner
- separate scaffold agent and reintegration agent on the same file
- separate orchestrator paperwork agent

If a single lead can do the file cleanly and a falsifier can verify it, stop there.

## Recommended Subagent Use Now That They Exist
OpenAI’s current Codex guidance is directionally clear even if it does not prescribe a giant multi-agent bureaucracy.

Official sources used:
- OpenAI, *How OpenAI uses Codex* (published 2025-11): `https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf`
- OpenAI Agents SDK: `https://openai.github.io/openai-agents-python/`
- OpenAI Agents SDK, Agent orchestration: `https://openai.github.io/openai-agents-python/multi_agent/`
- OpenAI Agents SDK, Handoffs: `https://openai.github.io/openai-agents-python/handoffs/`

Relevant official points:
- start with a plan for larger changes, then execute
- keep tasks well-scoped
- provide structure and context
- use `AGENTS.md` for persistent repo guidance
- use backlog/task-queue behavior for side tasks
- use Best-of-N when comparing alternative solutions
- OpenAI’s agent docs distinguish between manager-style orchestration and handoffs to specialist agents
- handoffs transfer control to a specialist; manager-style orchestration keeps one agent in control and calls specialists deliberately

My interpretation for repo docs work:
1. Subagents are useful for bounded, parallel, non-overlapping tasks.
2. They are not a reason to split one Markdown file across five writers.
3. The main agent should retain integration authority.
4. The best subagent uses in docs work are:
   - evidence extraction
   - link/path scans
   - remote/render verification
   - asset generation with a separate write scope
   - comparison of alternate nav/table layouts before one is chosen
5. If two agents need to edit the same Markdown file, the decomposition is wrong.

### Practical subagent pattern for derivative repos
Default to manager-style orchestration, not free-form handoffs.

Reason:
- documentation passes usually need one coherent integrator to preserve tone, structure, and truth boundaries
- handoffs are better when one specialist should fully take over a distinct domain
- docs work more often needs controlled sidecars than conversational takeover

Use at most three active lanes unless the repo is unusually large.

1. Lead doc integrator
- writes `README.md` and any shared core docs
- keeps control of the pass

2. Sidecar verifier
- scans links, anchors, GIF paths, and claim/evidence alignment

3. Sidecar specialist, only if needed
- either evidence mapper or asset/SVG implementer

That is usually enough.

Use a true handoff only when the next task is genuinely a different specialty with a disjoint output, for example a legal-governance annex or a standalone asset pack. Do not hand off a half-edited README just because another agent exists.

## Derivative Repo Build Standard
When another Zer0pa repo is created or upgraded, use ZPE-IMC as the structure/template source, not as the content source.

### Required behavior
1. Keep the same doc architecture where it makes sense.
2. Keep the same GIF/section-bar conventions initially.
3. Replace only repo-specific truth, metrics, proof paths, caveats, and downstream relationships.
4. Carry forward explicit honesty about:
   - what is verified
   - what is inferred
   - what is missing
   - what is owner-deferred
   - what is out of scope
5. Keep package/runtime/doc/legal surfaces separated.
6. Keep one canonical registry file for the repo and update it whenever the active doc surface changes.

### Minimum derivative-repo document set
Every derivative repo should, at minimum, create:
- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `LICENSE`
- `CITATION.cff`
- `ROADMAP.md` if there is downstream sequencing or gated decisions
- `GOVERNANCE.md` if evidence/status semantics matter publicly
- `docs/README.md`
- `docs/FAQ.md`
- `docs/SUPPORT.md`
- `docs/ARCHITECTURE.md` if there is a non-trivial runtime or contract model
- GitHub PR + issue templates

Add these when the repo needs them:
- auditor playbook
- public audit limits note
- legal boundaries note
- family/downstream contract docs
- governance/legal annexes equivalent to the SAL governance set

## Local And GitHub Review Discipline
Keep the workflow simple.

1. Local repo is the source of truth.
- Agents edit in the working repo first.
- The private or guinea-pig GitHub repo is for rendered review, not for ad hoc truth changes.

2. Push scoped files only.
- If the wave is README-only, push README-only plus any minimal assets it actually changed.

3. Keep one review lane unless there is a real integration reason not to.
- Branch sprawl made review state harder to reason about.
- If a repo uses `main` as the review branch, use that consistently. If it uses a dedicated review branch, use one only.

4. The review repo must match the approved local state.
- If local and remote differ, the work is not finished.

5. Do not treat the review repo as the place where content truth is invented.
- Truth should be established locally against proof and runtime artifacts, then published for review.

6. Spot-check the actual live rendered branch before declaring the standard frozen.
- Local file state is necessary.
- Live render state is also necessary.
- If a derivative repo is copying the standard, copy from the approved rendered state, not from an intermediate draft.

## Repo-Truth Rules For Derivative Repos
A repo derived from ZPE-IMC must answer these questions explicitly.

1. What is the front-door truth?
- What should an outsider believe after reading the README?

2. What is the current authority artifact?
- A manifest, proof report, benchmark, contract vector, or accepted run.

3. What is historical only?
- Frozen anchors, compatibility history, old demos, or chronology.

4. What is public truth versus operator/local truth?
- Do not blur them.

5. What is bounded or caveated?
- This includes licensing, partial modality support, missing hardware reruns, restricted datasets, or public/private surface differences.

6. What is the exact acquisition surface?
- Which GitHub repo/branch/snapshot should an outsider clone?
- Do not inherit ZPE-IMC’s acquisition surface if it is not true for that repo.

7. What is the one canonical authority block in the README?
- Decide where the promoted run, contract, or authority table lives.
- Avoid re-stating the same locked values in three later sections.

8. Which supporting doc owns each deeper concern?
- Architecture map
- audit procedure
- audit limits
- legal boundary
- contribution rules
- release gate

## Minimum QA Checklist Before A Doc Pass Can Be Called Good
1. All asset paths render on GitHub.
2. Root README has masthead plus the two additional GIFs; other docs have the shared masthead unless intentionally exempt.
3. Badge row, nav, section bars, and tables render cleanly.
4. README has one canonical promoted authority block rather than repeated metric warehouses.
5. No borrowed ZPE-IMC metrics remain in the derivative repo.
6. Links point to the repo’s actual current paths.
7. Acquisition surface, repo URL, contact, and license identity are coherent across docs.
8. Legal, package, runtime, and public-audit statements do not contradict each other.
9. Current authority, historical anchors, and public snapshot truth are separated.
10. Tables integrate real information and are not decorative duplication.
11. Open gaps are named plainly.
12. One falsification pass is completed.
13. Review repo or private GitHub mirror matches the local approved doc state.
14. Live GitHub rendering has been spot-checked, not merely assumed from local Markdown.

## Recommended Single-Page Brief For Any Repo Agent
Use this when briefing an agent on a derivative repo.

```text
You are the docs owner for this repo.

Use ZPE-IMC as the documentation structure and quality reference, not as the content source.

Read first:
1. /Users/Zer0pa/ZPE/ZPE-IMC/agent_ops/ZER0PA_REPO_DOCS_PLAYBOOK_CANONICAL_2026-03-21.md
2. The target repo's current README, CHANGELOG, CONTRIBUTING, SECURITY, LICENSE, CITATION, docs/README, docs/FAQ, docs/SUPPORT, and docs/ARCHITECTURE if present.
3. The target repo's current proof/runtime/contract artifacts.
4. The target repo's AGENTS.md.

Rules:
- Tell the truth about this repo only.
- Keep the ZPE-IMC visual conventions initially, including the shared masthead GIF and section-bar system.
- Keep the two extra GIF slots only in the root README.
- Do not inherit ZPE-IMC metrics, statuses, proof claims, acquisition links, or caveats unless they are also true in this repo.
- Use tables where they improve scan speed or boundary clarity.
- Separate front-door truth, public-audit truth, operator/local truth, and historical anchors.
- Use subagents only for bounded, non-overlapping work.
- One agent owns each edited file.
- One falsification pass is mandatory before publish.

Required outputs:
- updated canonical-doc registry for the target repo
- updated README and supporting docs as needed
- one short falsification report listing unsupported claims, path issues, or remaining owner inputs
```

## Evidence Used For This Playbook
- `/Users/Zer0pa/ZPE-IMC-REPO/agent_ops/repo_augmentation_wave_20/artifacts/WP_B/CANONICAL_DOC_SET_POST.tsv`
- `/Users/Zer0pa/ZPE-IMC-REPO/agent_ops/HANDOVER_REPO_AUGMENTATION_ORCHESTRATOR_2026-03-05.md`
- `/Users/Zer0pa/ZPE/ZPE-IMC/agent_ops/ZER0PA_REPO_DOCS_PLAYBOOK.md`
- `/Users/Zer0pa/ZPE/ZPE-IMC/agent_ops/HANDOVER_REPO_DOCS_STATE_AND_REPO_INSPECTOR_PROMPT_2026-03-02.md`
- `/Users/Zer0pa/ZPE/ZPE-IMC/agent_ops/readme_layout_wave_8/GITHUB_DOCS_DESIGN_PLAYBOOK_GOLD_STANDARD.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/README.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/AUDITOR_PLAYBOOK.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/PUBLIC_AUDIT_LIMITS.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/docs/ARCHITECTURE.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/docs/README.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/docs/family/IMC_INTERFACE_CONTRACT.md`
- `/Users/Zer0pa/ZPE-IMC-REPO/docs/family/IMC_RELEASE_NOTE_FOR_BIO_IOT.md`
- OpenAI official source: `https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf`
- OpenAI Agents SDK: `https://openai.github.io/openai-agents-python/`
- OpenAI Agents SDK, Agent orchestration: `https://openai.github.io/openai-agents-python/multi_agent/`
- OpenAI Agents SDK, Handoffs: `https://openai.github.io/openai-agents-python/handoffs/`
