# ZPE-Robotics

> Product-page mirror for `/encoding/ZPE-Robotics/`.
> Live public repo: [Zer0pa/ZPE-Robotics](https://github.com/Zer0pa/ZPE-Robotics).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
187x robot-motion compression. Searchable joint-stream archives. VLA token export. Bounded-lossy replay for smooth trajectories. Install from PyPI: `pip install zpe-robotics
- Public package acquisition route is `pip install zpe-robotics`; package
pip install zpe-robotics
pip install -e .
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
python -m pytest tests -q
```

## Product Page Mirror

**Product-page title:** ZPE-Robotics · Bounded-lossy motion archive with decoded primitive search · Zer0pa

**Product-page description:** ZPE-Robotics · bounded-lossy robot motion archive · 187× compression on LeRobot real data with decoded PrimitiveIndex search and VLA token export · 4/5 B-checks PASS · B3 bit-exact/search-without-decode MISS · PyPI v0.1.1 stale · source SAL-7.1

### Hero Translation

> 00 · ZPE-ROBOTICS · MOVEMENT MEMORYDEVELOPER-READY · B3 OPEN Robots that learn like humans do. A movement memory for robots — the form of an action, kept · ZPE-Robotics · PyPI zpe-robotics v0.1.1 · github.com/Zer0pa/ZPE-Robotics A person learns a waltz, a kung fu form, or how to pick something up the same way — by repeating the movement until its shape settles into the body. What stays is not one attempt; it is the form. Robots have never had a memory for that. ZPE-Robotics is one: it keeps the form of an action — pick, wipe, push, pull — so a robot can hold a movement, search it, and learn from it. Proven on smooth motion, real LeRobot data, at 187×.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-Robotics/ |
| Live public repository | https://github.com/Zer0pa/ZPE-Robotics |
| Repo identity used here | ZPE-Robotics |
| Website display identity | ZPE-Robotics |
| Verdict | BLOCKED |
| Posture | always_in_beta |
| Headline metric | 187.1345x compression on bounded robot joint-stream surface; 3-dataset spread 58.70x-186.05x (median 61.27x); encode p50 0.111 ms; decode p50 0.089 ms. Source: proofs/enterprise_benchmark/benchmark_result.json. |
| Honest blocker | The live package and bounded benchmark surface are useful now for bounded-lossy robot joint-stream archiving, decoded PrimitiveIndex search, and VLA token export. Full release readiness still depends on B3 step/discontinuous input closure (current 68-degree RMSE on unit-amplitude step inputs), bit-exact round-trip proof, and independent third-party reproduction. Search-without-decode is not proven: PrimitiveIndex requires full packet decode before indexing. |
| Mechanics asset from product page | ROBOTICS.gif |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| COMPRESSION | 187×† | LeRobot real-data benchmark; full baselines in Competitive Benchmarks section |
| ENCODE_P50 | 0.11 ms | per 1 000 frames, gate B4 PASS |
| DECODE_P50 | 0.089 ms | per 1 000 frames, gate B5 PASS |
| BENCHMARK_GATES | 4/5 | 3 datasets, 3 families; B3 (bit-exact) fails |

## Proof Anchors

| Path | State |
| --- | --- |
| proofs/ENGINEERING_BLOCKERS.md | VERIFIED |
| proofs/narrow_claim/NARROW_CLAIM_GATE.json | VERIFIED |
| proofs/enterprise_benchmark/GATE_VERDICTS.json | VERIFIED |
| proofs/red_team/red_team_report.json | VERIFIED |
| proofs/release_candidate/clean_clone_result.json | VERIFIED |
| proofs/release_candidate/it04_parity_matrix_result.json | VERIFIED |

## What We Prove

- Spectral wire transport with directional reasoning layer for robot action sequences
- Search operates on decoded motion streams via PrimitiveIndex
- Red-team resilience: 4 attacks withstand, 1 fails, 1 partially withstands, 1 remains open
- VLA tokenization aligns with vision-language-action model input formats
- Public package acquisition route is pip install zpe-robotics; package availability does not change blocker status

## What We Do Not Claim

- Full release readiness
- Bit-exact .zpbot round-trip replay
- B3 benchmark gate pass
- Red-team attack 3 lossless qualification
- General anomaly readiness beyond the declared threshold-selected holdout surface
- Robotics Rust ABI
- Independent third-party reproduction
- Generally valid ≤ 0.5° angular fidelity — the figure comes from smooth-trajectory slices only; FFT-based encoding causes Gibbs ringing on step/discontinuous inputs (68° RMSE measured on a unit-amplitude step signal)
- Search-without-decode — PrimitiveIndex requires full packet decode before indexing

## Blockers / Failures

> The live package and bounded benchmark surface are useful now for bounded-lossy robot joint-stream archiving, decoded PrimitiveIndex search, and VLA token export. Full release readiness still depends on B3 step/discontinuous input closure (current 68-degree RMSE on unit-amplitude step inputs), bit-exact round-trip proof, and independent third-party reproduction. Search-without-decode is not proven: PrimitiveIndex requires full packet decode before indexing.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
| V_01 | BENCHMARK_GATE_B1_COMPRESSION | PASS |
| V_02 | BENCHMARK_GATE_B2_ZSTD_BASELINE | PASS |
| V_03 | BENCHMARK_GATE_B3_BIT-EXACT_+_SE... | FAIL |
| V_04 | BENCHMARK_GATE_B4_ENCODE_LATENCY | PASS |
| V_05 | BENCHMARK_GATE_B5_DECODE_LATENCY | PASS |
| V_06 | RED-TEAM_ATTACK_1_BASELINE | PASS |
| V_07 | RED-TEAM_ATTACK_2_ENTROPY | PASS |
| V_08 | RED-TEAM_ATTACK_3_LOSSLESS_QUALI... | FAIL |
| V_09 | RED-TEAM_ATTACK_4_CORPUS_ADEQUACY | INC |
| V_10 | RED-TEAM_ATTACK_5_FALSE-POSITIVE... | PASS |
| V_11 | RED-TEAM_ATTACK_6_PYTHON_3.12_PA... | PASS |
| V_12 | RED-TEAM_ATTACK_7_EXTERNAL_REPRO... | INC |

## License

| Field | Value |
| --- | --- |
| License | LicenseRef-Zer0pa-SAL-7.1 |
| Authority source | proofs/ENGINEERING_BLOCKERS.md |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Research-Deferred — Investigation Underway | Step-input Gibbs ringing fix (B3 gate). Highest-value research investment. Investigation: discontinuity-aware primitive (pre-detect step → switch encoding regime), or hybrid lossless fallback for step segments. Lane scoped to smooth-trajectory bounded-lossy slices. |
| Operations / External Dependency | Third-party reproduction (Attack 7). INCONCLUSIVE pending independent run; surface contact requested. |

## Related Repos

No related repos are declared on the product page frontmatter.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-ROBOTICS · MOVEMENT MEMORYDEVELOPER-READY · B3 OPEN Robots that learn like humans do. A movement memory for robots — the form of an action, kept · ZPE-Robotics · PyPI zpe-robotics v0.1.1 · github.com/Zer0pa/ZPE-Robotics A person learns a waltz, a kung fu form, or how to pick something up the same way — by repeating the movement until its shape settles into the body. What stays is not one attempt; it is the form. Robots have never had a memory for that. ZPE-Robotics is one: it keeps the form of an action — pick, wipe, push, pull — so a robot can hold a movement, search it, and learn from it. Proven on smooth motion, real LeRobot data, at 187×.

### Bento Cell 2

> 01 · THE GAPRECORDED, NOT LEARNED A robot records a movement perfectly, yet cannot learn it — a recording is not a memory.

### Bento Cell 3

> 02 · MARKETSADJACENT FORECASTS Robot software — ’31 — $67.9B · Digital twin — ’30 — $155.8B · Warehouse robotics — ’30 — $17.3B · Industrial robotics — ’30 — $16.5B · AMR — ’30 — $8.7B · source: Next Move Strategy, MarketsandMarkets Every robot that learns to move works inside these markets; ZPE-Robotics is the memory beneath them.

### Bento Cell 4

> 03 · VALUE 187× Compression vs zstd_l19 on real LeRobot joint streams · bounded-lossy smooth motion

### Bento Cell 5

> 04 · INSIGHT Practiced enough, a movement leaves one thing behind: its form.

### Bento Cell 6

> 05.1 · CURRENT TECHRECORDED AND SHELVED Today a robot's movement gets dumped into ROS bagfiles or parquet. The files are large, findable only by timestamp or filename, never by the movement itself. Nothing downstream can learn from a recording it cannot read.

### Bento Cell 7

> 05.2 · OUR TECHKEEP THE FORM ZPE-Robotics keeps the form. It encodes a robot's movement into a bounded-lossy archive — keeping the shape of the action, dropping the once-only noise — at 187× on real LeRobot data. PrimitiveIndex returns runs by the movement inside them: every clean reach, every dropped grasp, every recovered pour. Pick, wipe, push, pull become findable, not just stored.

### Bento Cell 8

> 05.3 · BENCHMARKSLEROBOT REAL DATA Compression187.13× vs zstd_l19 Encode P500.111ms / 1k frames Decode P500.089ms / 1k frames Checks4/5archive suite B1 compressionPASS B2 zstd baselinePASS Replay + searchOPEN Scope: 3 LeRobot datasets; 58.70–186.05× spread. General replay and search remain open.

### Bento Cell 9

> 06 · MEASUREMENTMEASURED ARCHIVE SURFACE Archive claims stay tied to real LeRobot slices and smooth-motion limits.

### Bento Cell 10

> 06.1 · COMPARATIVE PERFORMANCE · LEROBOT BYTES PER FRAME ZPE-Robotics187.13× smaller zstd_l194.59× vs raw zstd_l34.44× vs raw raw float321.00× baseline LeRobot declared episodes (columbia_cairlab_pusht_real, 136 episodes, 27,808 frames), smooth-trajectory slices. Baselines are lossless zstd, gzip, lz4, MCAP, HDF5 variants. Spread across 3 datasets: 58.70–186.05×, median 61.27×. Source: proofs/enterprise_benchmark/benchmark_result.json.

### Bento Cell 11

> 07 · KEY METRICSMEASURED RESULTS

### Bento Cell 12

> 07.1 · COMPRESSION 187.13× vs zstd_l19 4.59× · bounded-lossy LeRobot data

### Bento Cell 13

> 07.2 · ENCODE P50 0.111ms per 1k frames · check B4 PASS

### Bento Cell 14

> 07.3 · DECODE P50 0.089ms per 1k frames · check B5 PASS

### Bento Cell 15

> 07.4 · ARCHIVE CHECKS 4 / 5PASS smooth archive PASS · general replay open

### Bento Cell 16

> 07.5 · DATASET SPREAD 61.27× median of 3 LeRobot datasets · 187.13× peak

### Bento Cell 17

> 08 · REPLAY FIDELITYSMOOTH VS STEP Smooth movement stays inside the archive boundary. Stepped movement does not.

### Bento Cell 18

> 08.1 · WHAT THE ARCHIVE SUPPORTSSMOOTH SLICE On smooth-trajectory slices of declared LeRobot data, movement encodes and decodes consistently across arm64, macOS and x86. A sharp or stepped movement does not: the FFT-based encoder rings — Gibbs distortion — measured at 68° RMSE on a unit-amplitude step. A step has no smooth form to keep. Search-without-decode and general bit-level replay remain open. PrimitiveIndex still walks decoded streams. The credibility claim is bounded-lossy smooth movement — useful for archive, analysis, and downstream teaching, not for live closed-loop control where every byte of the motion has to come back exactly.

### Bento Cell 19

> 08.2 · HONEST BLOCKER Honest Blocker · 187× is bounded-lossy on smooth movement; sharp, stepped movement still rings. General replay and search-without-decode are false. PrimitiveIndex requires decode. PyPI v0.1.1 is stale; zpe-motion-kernel is legacy; no Robotics Rust ABI. RT3 miss, RT4 partial, RT7 open.

### Bento Cell 20

> 09 WHEN MOVEMENT BECOMES MEMORY.

### Bento Cell 21

> 09.1 · THE AMBITION The aim is not a better robot policy — it is the memory underneath one. A robot that keeps the form of a movement can recall it, refine it, and pass it on. Demonstration stops being disposable capture and starts behaving like inventory a fleet can build on.

### Bento Cell 22

> 09.2 · WHAT WORKS NOW Working today, on smooth movement: 187× archives and recall by the shape of the action itself.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPEN Still open: bit-level replay, sharp-movement distortion, search without decode, independent reproduction, a current release.

### Bento Cell 24

> 09.4 · REPERTOIRE · NEAR-TERM (12–24 MO) A robot keeps every taught movement A teleoperation team that used to throw away demonstrations after training can now keep every pick, wipe, push, and pull. At 187× on smooth motion, a humanoid's entire taught repertoire fits in the space its raw logs used to take for one afternoon.

### Bento Cell 25

> 09.5 · RECALL · NEAR-TERM (12–24 MO) Engineers find runs by the movement A robotics platform engineer hunting a specific failure mode stops scrubbing video and grepping bag files. The archive returns every clean reach, every dropped grasp, every retry by the shape of the action — so the question “show me the bad pours” gets a direct answer.

### Bento Cell 26

> 09.6 · TEACHING · MID-TERM (24–48 MO) One robot's motion teaches the next A humanoid R&D lead exporting movements as vision-language-action tokens hands a taught skill straight into the next model generation. The form one robot kept after a thousand pours becomes the starting condition for the robot that hasn't poured anything yet.

### Bento Cell 27

> 09.7 · SIMULATION · MID-TERM (24–48 MO) Simulation gets real demonstrations back Once replay closes for stepped motion, a simulation team can rerun the actual factory floor inside their environment — the dropped boxes, the missed grasps, the recoveries — instead of synthesising plausible ones. Sim and reality converge around the same retained movement.

### Bento Cell 28

> 09.8 · APPRENTICESHIP · PARADIGM (48 MO+) Robots learn the way apprentices do When movement can be kept, searched, and faithfully replayed, a robot stops being trained by exposure and starts being taught the way a person learns a craft — holding each form, refining it across attempts, passing it to the next robot the way a master hands down a technique.

</details>

---

Source mapping: product route `/encoding/ZPE-Robotics/` -> live public repo `Zer0pa/ZPE-Robotics`. README generated from product-page authority plus retained install/dev commands only.
