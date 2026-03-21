<p>
  <img src="../../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Robotics Release Linkage

| Relation | Current truth | What it does not mean |
|---|---|---|
| documentation standard | Robotics uses IMC as the docs-layout and asset standard | Robotics does not inherit IMC claims, metrics, or status |
| proof taxonomy | proof, runbook, and historical separation follow the IMC model | no shared authority surface exists between the repos |
| runtime | current runtime coupling is none | no IMC package import and no robotics `.zpbot` Rust ABI are present today |
| release hygiene | governance and releasing patterns are aligned | Robotics is not a coupled multi-repo release system |
| future Rust lane | a later Rust-routing lane is possible | it is not current-state truth |

Current decision: treat Robotics as docs-linked and release-hygiene-linked to
IMC, not as a runtime-coupled system.
