<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# ZPBOT V2 Authority Surface

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

Date: 2026-03-17
Status: active Phase-2 protocol authority
Scope: first-lane deterministic motion-infrastructure artifact only

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

## Decision

`zpbot-v2` is externalized as a compatibility-profile authority surface over the current on-wire `CODEC_VERSION = 1` packet subset.

This is an explicit alias strategy, not a cosmetic rename:

- authority surface name: `zpbot-v2`
- compatibility mode: `wire-v1`
- on-wire magic: `ZPBOT`
- on-wire version byte: `1`

The v2 contract therefore means:

1. downstream tools and docs refer to the approved external surface as `zpbot-v2`;
2. the current deterministic packet bytes remain valid under the `wire-v1` compatibility profile;
3. any future byte-level lift to a new version number is out of scope until it preserves lossless compatibility and does not widen into v3 semantics.

## Frozen Packet Contract

<p>
  <img src="../.github/assets/readme/section-bars/compatibility-commitments.svg" alt="COMPATIBILITY COMMITMENTS" width="100%">
</p>

Header layout:

- format: `<5sB I H H I>`
- fields, in order:
  - `magic`
  - `wire_version`
  - `frame_count`
  - `joint_count`
  - `keep_coeffs`
  - `payload_crc32`

Payload:

- compressed `float32` real and imaginary FFT coefficients
- `zlib` compressed
- deterministic CRC32 check on the compressed bytes

## Independent Parsing Requirement

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

Phase 2 adds an independent parser in `src/zpe_robotics/wire.py`.

The parser is authoritative for:

- header parsing
- version validation
- CRC validation
- payload decompression
- deterministic reconstruction of the trajectory array

This keeps the external contract readable without relying on hidden local encoder knowledge.

## Provenance Requirements

<p>
  <img src="../.github/assets/readme/section-bars/evidence.svg" alt="EVIDENCE" width="100%">
</p>

Any artifact that claims `zpbot-v2` evidence must surface:

- `authority_surface = zpbot-v2`
- `compatibility_mode = wire-v1`
- `wire_version = 1`
- source path
- hash or replay hash
- generation timestamp
- host platform

## Explicit Non-Goals

<p>
  <img src="../.github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

This authority surface does not add:

- v3 fields
- SE(3), contact, wrench, or cognition sidecars
- lossy compression modes
- broader replacement-lane semantics

## Acceptance Rule

<p>
  <img src="../.github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

`zpbot-v2` counts as Phase-2 runnable only when:

- this document exists,
- the parser in `src/zpe_robotics/wire.py` passes the packet tests,
- the runbook in `proofs/runbooks/RUNBOOK_GATE_IT01_V2_FORMALIZATION.md` remains executable.
