# Dataset Limits

- RoboMimic PH low-dimensional demonstrations are benchmark data, not live robot execution.
- The feature surface is robot state/action telemetry; object image observations are not used.
- This run does not evaluate imitation-policy improvement, perturbation recovery, or cross-embodiment execution.
- Transport and Tool Hang are contrast labels here, not downstream policy-transfer tasks.

## Episode Lengths
- `can`: min `82`, mean `116.03`, max `151`
- `lift`: min `36`, mean `48.33`, max `64`
- `square`: min `107`, mean `150.77`, max `236`
- `transport`: min `373`, mean `468.76`, max `714`
- `tool_hang`: min `332`, mean `479.81`, max `744`
