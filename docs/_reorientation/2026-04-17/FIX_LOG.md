# Reorientation Fix Log - 2026-04-17

## Drift

- [README.md:150](../../../README.md) - replaced the missing `CITATION.cff` route with the current legal-boundary doc.
- [README.md:259](../../../README.md) - replaced the missing `RELEASING.md` route with the current package/runtime boundary file.
- [README.md:268](../../../README.md) - removed routes to missing root policy docs and replaced them with the current audit, support, legal, and registry docs that actually ship in this checkout.
- [README.md:286](../../../README.md) - replaced the missing `proofs/README_LINEAGE_PATHS.md` route with the current historical-lineage index at `proofs/artifacts/historical/README.md`.
- [docs/README.md:72](../../README.md) - replaced the missing publishing runbook route with the current workflow definition at `.github/workflows/publish.yml`.
- [docs/SUPPORT.md:22](../../SUPPORT.md) - removed the missing publishing runbook reference and routed publisher setup questions to the current workflow plus the explicit owner-run UI step.
- [proofs/ENGINEERING_BLOCKERS.md:44](../../../proofs/ENGINEERING_BLOCKERS.md) - corrected the stale "without decode" wording so the prose matches the current decoded-search implementation.
- [docs/RELEASE_CANDIDATE.md:24](../../RELEASE_CANDIDATE.md) - aligned the release-candidate note with the decoded-search reality instead of the retired no-decode claim.

## Clarity

- [README.md:23](../../../README.md) - rewrote the opening product description so Robotics reads as a standalone encoding product with a live package surface and explicit open blockers.
- [docs/FAQ.md:24](../../FAQ.md) - replaced the defensive release-readiness framing with a direct engineering-posture answer.
- [docs/AUDITOR_PLAYBOOK.md:12](../../AUDITOR_PLAYBOOK.md) - reframed the audit intro around a live public beta surface with blocker-governed authority.
- [proofs/FINAL_STATUS.md:3](../../../proofs/FINAL_STATUS.md) - clarified that `FINAL_STATUS.md` is a preserved historical snapshot rather than current authority.

## Consistency

- [docs/ARCHITECTURE.md:35](../../ARCHITECTURE.md) - made the search/token layer explicit and aligned it with the README and novelty card.
- [docs/ARCHITECTURE.md:48](../../ARCHITECTURE.md) - scoped the 8-direction x 3-magnitude token layer to search and FAST export rather than the wire codec.
- [docs/README.md:8](../../README.md) - aligned the docs index with the standalone-product framing used in the front door.
- [docs/DOC_REGISTRY.md:20](../../DOC_REGISTRY.md) - rebuilt the registry around files that actually exist in the repo and marked `docs/RELEASE_CANDIDATE.md` as supporting rather than current authority.

## Framing

- [README.md:278](../../../README.md) - retired the implicit umbrella framing and recast Robotics as one standalone product in the ZPE portfolio.
- [README.md:298](../../../README.md) - replaced the "IMC is the umbrella integration layer" line with a sibling-reference framing.
- [docs/family/ROBOTICS_RELEASE_LINKAGE.md:11](../../family/ROBOTICS_RELEASE_LINKAGE.md) - recast the IMC relation as sibling products sharing release hygiene rather than a coupled system.
- [docs/market_surface.json:23](../../market_surface.json) - aligned the machine-readable family-position summary to the same portfolio-not-platform framing.

## Beta posture

- [README.md:89](../../../README.md) - replaced the negative release-posture line with "useful now, improving continuously" while keeping the blockers sovereign.
- [docs/PUBLIC_AUDIT_LIMITS.md:11](../../PUBLIC_AUDIT_LIMITS.md) - rewrote the opening boundary in public-beta terms instead of release-ready negation.
- [docs/LEGAL_BOUNDARIES.md:19](../../LEGAL_BOUNDARIES.md) - replaced "not complete / release-ready" wording with direct blocker and verdict language.
- [CHANGELOG.md:19](../../../CHANGELOG.md) - recorded the ethos reorientation explicitly and softened historical "private-staging" prose without rewriting the historical version label.

## Primitive scope

- [README.md:64](../../../README.md) - made the 8-direction x 3-magnitude token layer explicit in the front-door proof surface.
- [docs/_reorientation/2026-04-17/NOVELTY_CARD.md:1](./NOVELTY_CARD.md) - documented the code-backed primitive scope and novelty surface for the downstream license pass.

## Honest limits

- [README.md:72](../../../README.md) - kept the open blocker surface explicit by naming the missing closed-engineering verdict directly.
- [proofs/ENGINEERING_BLOCKERS.md:8](../../../proofs/ENGINEERING_BLOCKERS.md) - preserved the blocker-state verdict while removing weaker defensive phrasing.
- [proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md:8](../../../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md) - kept the repo scoped to its real public beta wedge and rejected broader stack claims.
