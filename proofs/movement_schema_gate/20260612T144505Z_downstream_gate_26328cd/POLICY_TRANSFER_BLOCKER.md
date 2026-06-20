# Policy Transfer Blocker

Status: not run.

No policy training, policy finetuning, live robot execution, or cross-embodiment retargeting is run in this phase. The emitted downstream utility is action-imitation/adaptation error on frozen RoboMimic trajectories.

Consequences:

- no policy-transfer claim is allowed;
- no `transfer_eval.json` is emitted;
- `downstream_utility_eval.json` is the authority artifact for this phase;
- README claims remain frozen.
