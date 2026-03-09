#!/usr/bin/env python
"""Deterministic MuJoCo parity probe for ZPE Robotics max-wave Gate M3."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MuJoCo parity probe")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260220)
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--rmse-threshold-mm", type=float, default=0.1)
    parser.add_argument("--max-abs-threshold-mm", type=float, default=0.25)
    return parser.parse_args()


def _build_chain_xml(link_lengths: np.ndarray) -> str:
    dof = int(link_lengths.shape[0])
    lines: list[str] = [
        "<mujoco model='zpe_chain'>",
        "  <compiler angle='radian' coordinate='local'/>",
        "  <option gravity='0 0 0' timestep='0.002'/>",
        "  <worldbody>",
    ]

    indent = "    "
    for idx in range(dof):
        parent_pos = "0 0 0" if idx == 0 else f"{link_lengths[idx-1]:.6f} 0 0"
        lines.append(f"{indent}<body name='link_{idx}' pos='{parent_pos}'>")
        lines.append(
            f"{indent}  <joint name='joint_{idx}' type='hinge' axis='0 0 1' limited='false'/>"
        )
        lines.append(
            f"{indent}  <geom name='geom_{idx}' type='capsule' fromto='0 0 0 {link_lengths[idx]:.6f} 0 0' size='0.004'/>"
        )
        if idx == dof - 1:
            lines.append(f"{indent}  <site name='ee' pos='{link_lengths[idx]:.6f} 0 0' size='0.004'/>")
        indent += "  "

    for _ in range(dof):
        indent = indent[:-2]
        lines.append(f"{indent}</body>")

    lines.extend(["  </worldbody>", "</mujoco>"])
    return "\n".join(lines)


def _analytic_fk(qpos: np.ndarray, link_lengths: np.ndarray) -> np.ndarray:
    cumulative = np.cumsum(qpos, axis=1)
    x = np.sum(np.cos(cumulative) * link_lengths[None, :], axis=1)
    y = np.sum(np.sin(cumulative) * link_lengths[None, :], axis=1)
    z = np.zeros_like(x)
    return np.stack([x, y, z], axis=1)


def main() -> None:
    args = parse_args()

    import mujoco  # Imported lazily so import errors become explicit runtime evidence.

    link_lengths = np.linspace(0.20, 0.05, 6, dtype=np.float64)
    xml = _build_chain_xml(link_lengths)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ee")

    rng = np.random.default_rng(args.seed)
    qpos = rng.uniform(-1.2, 1.2, size=(args.samples, model.nq)).astype(np.float64)

    mujoco_xyz = np.zeros((args.samples, 3), dtype=np.float64)
    for i in range(args.samples):
        data.qpos[: model.nq] = qpos[i]
        mujoco.mj_forward(model, data)
        mujoco_xyz[i] = np.asarray(data.site_xpos[site_id], dtype=np.float64)

    analytic_xyz = _analytic_fk(qpos[:, : link_lengths.shape[0]], link_lengths)
    diff = mujoco_xyz - analytic_xyz
    rmse_mm = float(np.sqrt(np.mean(np.square(diff))) * 1000.0)
    max_abs_mm = float(np.max(np.abs(diff)) * 1000.0)

    status = "PASS" if (rmse_mm <= args.rmse_threshold_mm and max_abs_mm <= args.max_abs_threshold_mm) else "FAIL"
    report = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "status": status,
        "thresholds": {
            "rmse_mm_max": args.rmse_threshold_mm,
            "max_abs_mm_max": args.max_abs_threshold_mm,
        },
        "metrics": {
            "rmse_mm": rmse_mm,
            "max_abs_mm": max_abs_mm,
            "samples": args.samples,
            "dof": int(model.nq),
        },
        "runtime": {
            "python": platform.python_version(),
            "machine": platform.machine(),
            "mujoco_version": mujoco.__version__,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
