# ZPE-Robotics Novelty Card

**Product:** ZPE-Robotics
**Domain:** Deterministic archival, replay, search, and token export for robot joint-motion trajectories.
**What we sell:** Searchable motion archives with compressed replay, audit-friendly packet boundaries, and VLA token export for robotics infrastructure teams.

## Novel contributions

1. **Frozen `.zpbot` motion packet contract for robotics telemetry** — ZPE-Robotics defines a deterministic packet surface that freezes a robotics-oriented FFT/zlib archive into an auditable `zpbot-v2` / `wire-v1` contract with explicit header fields, CRC checks, and reproducible decode semantics. Code: `src/zpe_robotics/codec.py:24-40`, `src/zpe_robotics/wire.py:50-137`. Nearest prior art (if known): generic FFT truncation, zlib-compressed binary payloads, and CRC-framed containers. What is genuinely new here: the productized combination of those standard pieces into a Robotics-specific motion archive contract with a named external authority surface, decode invariants, and audit-friendly metadata.
2. **Decoded-motion primitive retrieval over an 8-direction x 3-magnitude token layer** — PrimitiveIndex search reduces decoded trajectories into a compact directional token stream, combines histogram, shape, and suffix-overlap scoring, and searches frozen templates over committed `.zpbot` corpora. Code: `src/zpe_robotics/primitives.py:110-137`, `src/zpe_robotics/primitive_index.py:37-76`, `src/zpe_robotics/primitive_index.py:114-154`. Nearest prior art (if known): motion-template retrieval, histogram search, suffix-array retrieval. What is genuinely new here: the Robotics-specific token surface and scoring blend, tied directly to the repo's compressed packet artifacts and frozen primitive template set.
3. **Shared token surface across archive search, anomaly, and VLA export workflows** — The repo reuses the directional tokenization idea across FAST-style VLA export, per-file anomaly histograms, and LeRobot episode packaging so the same motion archive can support audit, retrieval, and model-facing export surfaces. Code: `src/zpe_robotics/vla_bridge.py:16-36`, `src/zpe_robotics/anomaly.py:46-77`, `src/zpe_robotics/lerobot_codec.py:35-64`. Nearest prior art (if known): action-token export pipelines, dataset wrappers, and z-score anomaly detection. What is genuinely new here: the way ZPE-Robotics binds those workflows to the same packetized motion surface and provenance-bearing episode sidecars rather than treating them as unrelated adapters.

## Standard techniques used (explicit, not novel)

- FFT / inverse FFT truncation and reconstruction
- `zlib` compression
- CRC32 payload checks
- cosine similarity
- suffix arrays
- quantile binning
- z-score thresholding

## Compass-8 / 8-primitive architecture

NO — wire codec uses FFT + `zlib`; directional 8-dir × 3-mag tokens exist only in the search/token-export layer (see `src/zpe_robotics/primitives.py:110-129` and `src/zpe_robotics/vla_bridge.py:25-36`) but do not constitute the encoding substrate.

## Open novelty questions for the license agent

- Should the FAST-style token export in `src/zpe_robotics/vla_bridge.py:16-36` be scheduled as its own novelty item, or treated as an application surface of the same directional token layer already claimed for PrimitiveIndex search?
