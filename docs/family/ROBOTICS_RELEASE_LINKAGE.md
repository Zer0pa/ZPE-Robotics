# Robotics Release Linkage

## Current Relation To IMC

Robotics is using the IMC repo as a structural model for:

- front-door docs
- proof directory taxonomy
- audit-path shape
- public versus operator separation

## What This Does Not Mean

- it does not prove runtime coupling to IMC
- it does not prove a shared compatibility vector already exists
- it does not allow Robotics claims to inherit IMC proof status

## Current Decision

Treat Robotics as contract-linked for release hygiene and documentation shape.
Do not treat it as a runtime-coupled multi-repo system unless later evidence
proves that.
