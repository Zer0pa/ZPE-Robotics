"""Analytic kinematics helpers for fidelity evaluation."""

from __future__ import annotations

import numpy as np


def forward_kinematics_ee(
    joint_trajectory: np.ndarray,
    link_lengths: np.ndarray | None = None,
) -> np.ndarray:
    joints = np.asarray(joint_trajectory, dtype=np.float64)
    if joints.ndim != 2:
        raise ValueError("joint_trajectory must be 2D")
    frames, dof = joints.shape

    if link_lengths is None:
        link_lengths = np.linspace(0.20, 0.05, dof, dtype=np.float64)
    else:
        link_lengths = np.asarray(link_lengths, dtype=np.float64)

    if link_lengths.shape != (dof,):
        raise ValueError("link_lengths shape mismatch")

    cumulative = np.cumsum(joints, axis=1)
    x = np.sum(np.cos(cumulative) * link_lengths[None, :], axis=1)
    y = np.sum(np.sin(cumulative) * link_lengths[None, :], axis=1)
    z = 0.015 * np.sum(np.sin(joints[:, ::2]), axis=1)

    ee = np.stack([x, y, z], axis=1)
    if ee.shape != (frames, 3):
        raise RuntimeError("unexpected ee shape")
    return ee


def ee_rmse_mm(reference_joints: np.ndarray, reconstructed_joints: np.ndarray) -> float:
    ref_ee = forward_kinematics_ee(reference_joints)
    rec_ee = forward_kinematics_ee(reconstructed_joints)
    diff = ref_ee - rec_ee
    rmse_m = np.sqrt(np.mean(np.square(diff)))
    return float(rmse_m * 1000.0)


def rmse_deg(reference: np.ndarray, reconstructed: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.float64)
    rec = np.asarray(reconstructed, dtype=np.float64)
    if ref.shape != rec.shape:
        raise ValueError("shape mismatch")
    err = np.rad2deg(ref - rec)
    return float(np.sqrt(np.mean(np.square(err))))

