# OPERATOR_RUNBOOK

This file lists available CLI commands. Command availability does not imply
that engineering blockers are closed. Use `proofs/ENGINEERING_BLOCKERS.md` for
the current authority surface.

1. Install: `pip install zpe-motion-kernel`
2. Record a ROS2 bag with ZPE: `ros2 bag record -s zpe --all`
3. Compress an existing bag: `zpe encode input.bag output.zpbot`
4. Replay: `zpe decode output.zpbot replayed.bag`
5. Verify integrity: `zpe verify output.zpbot`
6. Search a trajectory library: `zpe search ./demos REACH`
7. Detect fleet anomalies: `zpe anomaly ./fleet_bags query.zpbot`
8. Compress a LeRobot dataset: `zpe lerobot-compress ./lerobot_data ./compressed`
9. Export VLA tokens: `zpe export-tokens trajectory.zpbot --format fast`
