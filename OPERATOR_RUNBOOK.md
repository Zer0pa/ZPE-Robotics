# ZPE Motion Kernel Operator Runbook

## Scope

This release candidate is a deterministic motion-kernel lane. It operates on the frozen `.zpbot` packet surface and the deterministic `ZPBAG1` proof envelope. It does not yet claim native rosbag2 directory support.

## Record

Start from a deterministic single-record bag envelope:

```bash
zpe encode input.bag output.zpbot
```

`input.bag` must contain exactly one deterministic `ZPBAG1` record.

## Replay

Decode a packet back into a single-record proof envelope:

```bash
zpe decode output.zpbot replay.bag
```

## Verify

Run CRC and packet-hash verification:

```bash
zpe verify output.zpbot
```

This exits non-zero if the packet is malformed or fails integrity checks.

## Inspect

Print frozen header fields:

```bash
zpe info output.zpbot
```

## Current Limits

- current bag lane: deterministic single-record `ZPBAG1`
- hosted ROS2 runtime proof: separate, already carried by the hosted `M1` artifact
- cross-platform parity: validated separately through hosted parity artifacts
