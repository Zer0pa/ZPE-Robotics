<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# FAQ

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

Short answers about the current ZPE-Robotics package, blocker state, and
release boundary.

<p>
  <img src="../.github/assets/readme/section-bars/questions.svg" alt="QUESTIONS" width="100%">
</p>

## Is this repo public-release ready?

No. Engineering remains incomplete. Benchmark gate `B3` fails, red-team attacks
`3` and `5` fail, attack `4` only partially withstands, and the robotics
`.zpbot` path is not routed through a current ZPE-IMC Rust ABI.

## What is actually green right now?

The technical release surface is aligned for the standalone package wedge, and
benchmark gates `B1`, `B2`, `B4`, and `B5` pass. Red-team attacks `1`, `2`,
and `6` also withstand.

## What is still blocked?

The governing blockers are:

- `B3` because searchability is present but strict bit-exact replay is not
- red-team attack `3` because strict `np.array_equal` fails on the current
  round-trip path
- red-team attack `5` because the nominal false-positive rate is `0.2`
- current Python encode/decode still does not route through a robotics Rust ABI
- external third-party reproduction remains open

## Is the package available today?

Yes. The current package acquisition surface is `pip install zpe-motion-kernel`.
That does not change blocker status.

## Why can package metadata look greener than these docs?

The `0.1.0` package description on PyPI reflects the March 18 release metadata.
The repo docs were updated on March 21 to reflect the later blocker-state
evidence. Until a new package release is intentionally cut, the repo docs are
the current authority for engineering status.

## Is this repo using ZPE-IMC at runtime?

No. IMC is the documentation and release-hygiene reference model for this repo.
It is not a current runtime dependency, and no robotics `.zpbot` Rust ABI is
wired into this package today.

## Are the historical proof bundles still current?

No. They are lineage only. Keep them for provenance, not for current status.

## What real data supports the benchmark story?

The current real-dataset benchmark used `lerobot/columbia_cairlab_pusht_real`
and reported `187.1345x` compression. That result is real, but it is still
bounded because the corpus run used `136` episodes at `10 Hz`, below the
`200` episode / `50 Hz` target.

<p>
  <img src="../.github/assets/readme/section-bars/faq-and-support.svg" alt="FAQ AND SUPPORT" width="100%">
</p>

If your question is not answered here:

- support routing: `SUPPORT.md`
- audit route: `AUDITOR_PLAYBOOK.md`
- release boundary: `../RELEASING.md`
