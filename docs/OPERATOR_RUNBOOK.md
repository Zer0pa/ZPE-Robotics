<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# OPERATOR_RUNBOOK

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This file lists available CLI commands. Command availability does not imply
that engineering blockers are closed. Use `../proofs/ENGINEERING_BLOCKERS.md` for
the current authority surface.

<p>
  <img src="../.github/assets/readme/section-bars/quick-start.svg" alt="QUICK START" width="100%">
</p>

| Need | Command |
|---|---|
| install | `pip install zpe-robotics` |
| record a ROS2 bag with ZPE | `ros2 bag record -s zpe --all` |
| compress an existing bag | `zpe encode input.bag output.zpbot` |
| replay | `zpe decode output.zpbot replayed.bag` |
| verify integrity | `zpe verify output.zpbot` |
| search a trajectory library | `zpe search ./demos REACH` |
| detect fleet anomalies | `zpe anomaly ./fleet_bags query.zpbot` |
| compress a LeRobot dataset | `zpe lerobot-compress ./lerobot_data ./compressed` |
| export VLA tokens | `zpe export-tokens trajectory.zpbot --format fast` |
