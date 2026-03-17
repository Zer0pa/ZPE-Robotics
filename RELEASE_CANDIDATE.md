# RELEASE_CANDIDATE

## v0.1.0 — 2026-03-17

- Storage reduction on the frozen arm fixture: `238.02421307506054x`.
- ARM64 portable: hosted ARM64 parity matched the frozen reference hash.
- Bit-perfect replay: hosted parity and bridge evidence preserve `a0941be23dc19bf96d7ec2e25f7ede9c051c3b28f51f141b89fdfc2691c3e125`.
- Hostile-path auditable: corrupted magic, CRC mismatch, and truncated payloads fail explicitly.
- Clean-clone evidence hash: `9c2a23c865b575b5ee29bcfbfba982201ee7010a43eed61860549bc25cd542aa`.

## What it is

`zpe-motion-kernel` is a drop-in deterministic motion kernel for frozen `zpbot-v2` / `wire-v1` transport, replay, and integrity verification. The current release candidate is a private source-installable utility artifact that compresses deterministic motion data, preserves bit-stable replay surfaces, and exposes an auditable CLI without claiming to replace an end-to-end robotics stack.

## Proven claims

- Storage reduction on the frozen arm fixture: `238.02421307506054x` versus the comparator-side raw float32 storage surface.
- ARM64 portable: hosted ARM64 parity matched the frozen reference hash.
- Bit-perfect replay: hosted parity and bridge evidence preserve the frozen `a0941be23dc19bf96d7ec2e25f7ede9c051c3b28f51f141b89fdfc2691c3e125` hash.
- Hostile-path auditable: corrupted magic, CRC mismatch, and truncated payload all fail explicitly with preserved error reporting.

## What it does NOT claim yet

- Policy superiority over learned-policy systems.
- Full-stack robotics replacement.
- Jetson-native proof.
- Public package-index availability for `pip install zpe-motion-kernel`.

## How to install

Package name: `zpe-motion-kernel`

Intended published install command:

```bash
pip install zpe-motion-kernel
```

Clean-clone verification proves the source-install path that is already committed:

```bash
pip install -e .
```

## The four evidence hashes

- `M1` artifact: `proofs/release_candidate/m1_ros2_probe_result.json`
  SHA-256: `640a203ac1701dde6e9aa507a2b3c49c1a7a844e03a87070453e50b1326f8d0d`
- `ARM64` artifact: `proofs/release_candidate/arm64_parity_result.json`
  SHA-256: `3c90616efbfcb9d8f24f0d55dac213272289922e5df4821bd5b658a5ec9f643f`
- `IT-03/05` artifact: `proofs/release_candidate/it03_it05_composition_result.json`
  SHA-256: `58e27c6f51f70562f14f83baabd917f4f972f6702046d8c049b8e4f058347dcb`
- `E-G3` artifact: `proofs/release_candidate/e_g3_comparator_result.json`
  SHA-256: `7ee62646487b4b5f76c6690838a268bd77b08499e05d15f1ab3f9edc943a1b99`

## License

Zer0pa SAL v6.0 — free under `$100M` revenue, commercial license required above.
