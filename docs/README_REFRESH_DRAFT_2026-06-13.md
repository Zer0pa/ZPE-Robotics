# ZPE-Robotics

## Package Install

Installable package: `pip install zpe-robotics`.
Source: [Zer0pa/ZPE-Robotics](https://github.com/Zer0pa/ZPE-Robotics/).

```bash
pip install zpe-robotics
```

For full install, smoke, source, and developer commands, [click here](#install-developer-commands-detailed).

---

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><span><b>00 · ZPE-ROBOTICS · MOVEMENT MEMORY</b></span> <span>DEVELOPER-READY · B3 OPEN</span></div>
      <h1>Robots That Learn From The Shape Of Failure.</h1>
      <p>A movement memory lab for robots &mdash; the form of an action, tested until only evidence remains · ZPE-Robotics · PyPI <em>zpe-robotics</em> v0.1.1 · github.com/Zer0pa/ZPE-Robotics</p>
      <p>A person learns a waltz, a tool grip, or how not to drop a cup by repeating the movement until its shape, limits, and mistakes settle into the body. What stays is not one recording; it is the form, plus the scar of what failed. ZPE-Robotics keeps that evidence in code. The smooth-motion archive is proven at <strong>187&times;</strong>; newer nature-primitive candidates for schema, curation, and forensics have failed their gates and remain first-class artifacts, not claims.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<figure>
        <div><img src="docs/assets/product-page-mechanics.gif" alt="ZPE-Robotics approved scientific square mechanics diagram showing wire-v1 motion codec and VLA bridge mechanics."></div>
        <figcaption><b>Scope:</b> bounded-lossy smooth movement archive. No live closed-loop control, no general bit-level replay, no production forensics claim.</figcaption>
      </figure>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>01 · THE GAP</b> <span>RECORDED, NOT LEARNED</span></div>
      <h2>A robot records a movement perfectly, yet cannot tell which form mattered, which failure taught anything, or which primitive deserves to survive.</h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>02 · MARKETS</b> <span>ADJACENT FORECASTS</span></div>
      <div>Robot software &mdash; &rsquo;31 &mdash; $67.9B · Digital twin &mdash; &rsquo;30 &mdash; $155.8B · Warehouse robotics &mdash; &rsquo;30 &mdash; $17.3B · Industrial robotics &mdash; &rsquo;30 &mdash; $16.5B · AMR &mdash; &rsquo;30 &mdash; $8.7B · <em>source:</em> Next Move Strategy, MarketsandMarkets</div>
      <div>Every robot that learns from movement works inside these markets; ZPE-Robotics is the evidence layer beneath them.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="50%" valign="top">
<div><b>03 · VALUE OF MARKET</b></div>
      <div>187<span>&times;</span></div>
      <div>Compression vs zstd_l19 on real LeRobot joint streams &middot; <b>bounded-lossy smooth motion</b></div>
</td>
<td width="50%" valign="top">
<div><b>04 · INSIGHT</b></div>
      <h2>Practiced enough, a movement leaves two things behind: <span>its form and its failures.</span></h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="50%" valign="top">
<div><b>05.1 · CURRENT TECH</b> <span>RECORDED AND SHELVED</span></div>
        <p>Today a robot's movement gets dumped into ROS bagfiles, HDF5, or parquet. The files are large, findable mostly by timestamp, filename, or labels, rarely by the movement itself. A failure becomes video to scrub, not evidence a system can reason over.</p>
</td>
<td width="50%" valign="top">
<div><b>05.2 · OUR TECH</b> <span>KEEP THE FORM</span></div>
        <p>ZPE-Robotics keeps the form, then attacks its own primitives. It encodes smooth movement into a bounded-lossy archive at <strong>187&times;</strong> on real LeRobot data. It also ships the latest failed gates: movement schema did not earn a claim upgrade, functional curation lost to simple baselines, and telemetry-only episode forensics missed annotated failure windows. The negative result is part of the product surface: know what nature-shaped code has not yet earned.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>05.3 · BENCHMARKS</b> <span>LEROBOT REAL DATA</span></div>
      <div>
        <div>
          <div><span>Compression</span><b>187.13</b><small>&times; vs zstd_l19</small></div>
          <div><span>Encode P50</span><b>0.111</b><small>ms / 1k frames</small></div>
          <div><span>Decode P50</span><b>0.089</b><small>ms / 1k frames</small></div>
          <div><span>New gates</span><b>0/4</b><small>claim upgrades</small></div>
        </div>
        <div>
          <div><span>B1 compression</span>  <span>PASS</span></div>
          <div><span>B2 zstd baseline</span>  <span>PASS</span></div>
          <div><span>Schema / curation / forensics</span>  <span>NO UPGRADE</span></div>
        </div>
      </div>
      <div><b>Scope:</b> 3 LeRobot datasets; 58.70&ndash;186.05&times; spread. General replay, search without decode, and product-grade forensics remain open.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="34%" valign="top">
<div><b>06 · MEASUREMENT</b> <span>MEASURED ARCHIVE SURFACE</span></div>
      <h2>Archive claims stay tied to real LeRobot slices, smooth-motion limits, and failed gates that remain visible.</h2>
</td>
<td width="66%" valign="top">
<div><b>06.1 · COMPARATIVE PERFORMANCE &middot; LEROBOT BYTES PER FRAME</b></div>
      <div>
        <div>
          <div><span>ZPE-Robotics</span>  <span>187.13&times; smaller</span></div>
          <div><span>zstd_l19</span>  <span>4.59&times; vs raw</span></div>
          <div><span>zstd_l3</span>  <span>4.44&times; vs raw</span></div>
          <div><span>raw float32</span>  <span>1.00&times; baseline</span></div>
        </div>
      </div>
      <div>LeRobot declared episodes (<b>columbia_cairlab_pusht_real</b>, 136 episodes, 27,808 frames), smooth-trajectory slices. Baselines are lossless zstd, gzip, lz4, MCAP, HDF5 variants. Spread across 3 datasets: 58.70&ndash;186.05&times;, median 61.27&times;. Source: <em>proofs/enterprise_benchmark/benchmark_result.json</em>.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07 · KEY METRICS</b> <span>MEASURED RESULTS</span></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.1 · COMPRESSION</b></div>
      <div>187.13<span>&times;</span></div>
      <div>vs zstd_l19 4.59&times; &middot; <b>bounded-lossy LeRobot data</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.2 · ENCODE P50</b></div>
      <div>0.111<span>ms</span></div>
      <div>per 1k frames &middot; <b>check B4 PASS</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.3 · DECODE P50</b></div>
      <div>0.089<span>ms</span></div>
      <div>per 1k frames &middot; <b>check B5 PASS</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.4 · ARCHIVE CHECKS</b></div>
      <div>4 / 5<span>PASS</span></div>
      <div>smooth archive PASS &middot; <b>general replay open</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>07.5 · DATASET SPREAD</b></div>
      <div>61.27<span>&times;</span></div>
      <div>median of 3 LeRobot datasets &middot; <b>187.13&times; peak</b></div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>08 · REPLAY FIDELITY</b> <span>SMOOTH VS STEP</span></div>
      <h2>Smooth movement stays inside the archive boundary. Stepped movement and telemetry-only failure windows <span>do not.</span></h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="66%" valign="top">
<div><b>08.1 · WHAT THE ARCHIVE SUPPORTS</b> <span>SMOOTH SLICE</span></div>
      <p>On smooth-trajectory slices of declared LeRobot data, movement encodes and decodes consistently across arm64, macOS and x86. A sharp or stepped movement does not: the FFT-based encoder rings &mdash; Gibbs distortion &mdash; measured at <strong>68&deg; RMSE on a unit-amplitude step</strong>. A step has no smooth form to keep.</p>
      <p>Fresh gates add the next boundary. Movement-schema packets, functional curation, and incident traces are implemented, tested, and archived, but none cleared the sovereign gate. Raw, PCA, FFT, DCT, fixed-window, or nearest-demo baselines still dominate enough tasks to block any stronger public claim.</p>
</td>
<td width="34%" valign="top">
<div><b>08.2 · HONEST BLOCKER</b></div>
      <span>Honest Blocker &middot;</span>
      <p><strong>187&times; is bounded-lossy</strong> on smooth movement; sharp, stepped movement still rings. General replay and search-without-decode are false. Movement schema is narrow retrieval only; functional curation and forensics are abandoned as-is. PyPI v0.1.1 is stale; zpe-motion-kernel is legacy; no Robotics Rust ABI.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="33%" valign="top">
<div><b>09</b> </div>
      <h2>WHEN FAILURE BECOMES <span>MEMORY.</span></h2>
</td>
<td width="67%" valign="top">
<div><b>09.1 · THE AMBITION</b></div>
      <p>The aim is not a prettier robot log &mdash; it is a memory layer that keeps what a movement tried to become. A robot that keeps form and failure can recall, reject, refine, and pass on movement knowledge instead of treating every demonstration as disposable capture.</p>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="33%" valign="top">
<div><b>09.2 · WHAT WORKS NOW</b> </div>
        <h2>Working today: 187&times; smooth archives, decoded-shape retrieval, and auditable negative gates for rejected primitives.</h2>
</td>
<td width="67%" valign="top">
<div><b>09.3 · WHAT'S STILL OPEN</b> </div>
        <h2>Still open: bit-level replay, sharp-movement distortion, search without decode, product forensics, independent reproduction, a current release.</h2>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.4</b> &middot; REPERTOIRE &middot; NEAR-TERM (12&ndash;24 MO)</div>
      <div>A robot keeps every taught movement</div><div>A teleoperation team that used to throw away demonstrations after training can keep every smooth pick, wipe, push, and pull. At 187&times; on smooth motion, a humanoid's taught repertoire fits where raw logs used to hold one afternoon.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.5</b> &middot; RECALL &middot; NEAR-TERM (12&ndash;24 MO)</div>
      <div>Engineers find runs by the movement</div><div>A robotics platform engineer hunting a failure mode stops relying only on video scrub and filename search. The archive can return decoded runs by the shape of the action; the stronger promise, search without decode, remains blocked until it beats the baselines.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.6</b> &middot; TEACHING &middot; MID-TERM (24&ndash;48 MO)</div>
      <div>One robot's motion teaches the next</div><div>A humanoid R&amp;D lead exporting movements as vision-language-action tokens needs more than compression. The latest schema experiments say what is not enough yet: a nature-shaped primitive must beat nearest-demo and spectral baselines before it can become teaching substrate.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.7</b> &middot; SIMULATION &middot; MID-TERM (24&ndash;48 MO)</div>
      <div>Simulation gets real demonstrations back</div><div>Once replay and forensics close, a simulation team can rerun the actual factory floor inside its environment &mdash; the drops, misses, recoveries, and corrections &mdash; instead of inventing plausible ones. Today, that remains a target, not a claim.</div>
</td>
</tr>
</table>

<table width="100%">
<tr>
<td width="100%" valign="top">
<div><b>09.8</b> &middot; APPRENTICESHIP &middot; PARADIGM (48 MO+)</div>
      <div>Robots learn the way apprentices do</div><div>When movement can be kept, searched, replayed, and falsified, a robot stops being trained by exposure and starts being taught like a craft: hold the form, study the failed attempts, discard false primitives, and pass forward only what survives contact with evidence.</div>
</td>
</tr>
</table>

---

<a id="install-developer-commands-detailed"></a>

## Install / Developer Commands Detailed

#### Quick Start

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Repository | `https://github.com/Zer0pa/ZPE-Robotics.git` |
| Package / import / CLI | `zpe-robotics` / `zpe_robotics` / `zpe-robotics` |
| Acquisition surface | `pip install zpe-robotics` (available on PyPI) |
| License | `LicenseRef-Zer0pa-SAL-7.1` |
| Contact | `architects@zer0pa.ai` |
| Release state | public repo and published package; engineering surface remains blocker-governed |
| Engineering | not complete |
| Current authority | `proofs/forensics_gate/20260612T204151Z_forensics_pilot_26328cd/FINAL_GATE_VERDICT.json` |

| Authority layer | File |
|---|---|
| governing blocker state | `proofs/ENGINEERING_BLOCKERS.md` |
| smooth archive benchmark | `proofs/enterprise_benchmark/GATE_VERDICTS.json` |
| movement-schema verdicts | `proofs/movement_schema_gate/` |
| curation / functional / forensics verdicts | `proofs/curation_gate/`, `proofs/functional_curation_gate/`, `proofs/forensics_gate/` |
<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

Install from PyPI:

```bash
pip install zpe-robotics
zpe-robotics --version
```

Or install from source (development):

```bash
pip install -e .
zpe-robotics --version
```

Repo-local engineering surface:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
python -m pytest tests -q
python -m build
```

If you need the shortest honest verification route, use
`docs/AUDITOR_PLAYBOOK.md`.
If you need the release workflow boundary, use
`proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md`.

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

| Need | Route |
|---|---|
| Security reporting | `SECURITY.md` |
| Claim boundary | `docs/CLAIM_BOUNDARY.md` |
| Support routing | `docs/SUPPORT.md` |
| Docs index | `docs/README.md` |
| Operator commands | `docs/OPERATOR_RUNBOOK.md` |
