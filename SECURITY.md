<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Security Policy

<p>
  <img src=".github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

This document covers security reporting for the `zpe-motion-kernel` package,
its declared dependencies, its workflows, and the committed proof corpus.

What counts as a security issue here:

- secrets, credentials, or tokens committed into the repo or proof artifacts
- dependency vulnerabilities in the declared package dependencies
- supply-chain weaknesses in the build or publish workflows
- command or file-handling flaws that could lead to code execution, privilege
  escalation, or data exposure

What does not count as a security issue here:

- benchmark failures, replay failures, or falsification findings
- disagreements with the documented blocker-state or benchmark verdicts
- historical path residue in preserved historical bundles

<p>
  <img src=".github/assets/readme/section-bars/reporting-a-vulnerability.svg" alt="REPORTING A VULNERABILITY" width="100%">
</p>

Do not open a public issue for a security vulnerability.

| What to send | Where |
|---|---|
| private vulnerability report | `architects@zer0pa.ai` |
| affected component and version | include repo path or package name |
| reproduction details or proof of concept | include exact commands and expected impact |
| severity assessment | include confidentiality, integrity, or availability impact |
| suggested remediation | optional but useful |

<p>
  <img src=".github/assets/readme/section-bars/response-commitment.svg" alt="RESPONSE COMMITMENT" width="100%">
</p>

| Stage | Target timeframe |
|---|---|
| acknowledgement | within 48 hours |
| initial assessment | within 7 days |
| remediation or mitigation plan | within 30 days for confirmed issues |

<p>
  <img src=".github/assets/readme/section-bars/supported-versions.svg" alt="SUPPORTED VERSIONS" width="100%">
</p>

| Version | Supported |
|---|---|
| `main` | current private workstream branch |
| `0.1.0` | current package artifact |
| earlier private staging snapshots | not supported as active security targets |

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

- release-readiness disputes
- anomaly false-positive complaints that do not introduce a security impact
- requests to reinterpret blocker-state evidence as a release waiver
