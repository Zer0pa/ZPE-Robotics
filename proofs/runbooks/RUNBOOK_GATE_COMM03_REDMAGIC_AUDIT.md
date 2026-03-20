# Gate COMM-03 Runbook: RedMagic Audit Surface

## Objective

Preserve the bounded COMM-03 Mac-plus-RedMagic execution path by proving that the attached RedMagic 10 Pro+ can surface the canonical packet hash through foreground Termux without claiming device-native replay regeneration, ROS2 parity, certification, or RunPod involvement.

## Preconditions

- Repo root is `/Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`
- `proofs/release_candidate/canonical_release_packet.zpbot` exists on the Mac
- `proofs/comm03/comm03_provenance_manifest.json` already exists from the Mac audit bundle step
- ADB reaches the attached RedMagic device

## Commands

1. `adb devices -l`
2. `adb push proofs/release_candidate/canonical_release_packet.zpbot /sdcard/Download/canonical_release_packet.zpbot`
3. `adb push proofs/comm03/comm03_provenance_manifest.json /sdcard/Download/comm03_provenance_manifest.json`
4. `adb shell am start -n com.termux/.app.TermuxActivity`
5. `adb shell input text clear`
6. `adb shell input keyevent KEYCODE_ENTER`
7. `adb shell input text 'sha256sum%s/storage/emulated/0/Download/canonical_release_packet.zpbot'`
8. `adb shell input keyevent KEYCODE_ENTER`
9. `adb exec-out screencap -p > proofs/comm03/comm03_redmagic_termux_audit.png`

## Expected Output

- `proofs/comm03/comm03_redmagic_termux_audit.png`
- `proofs/comm03/comm03_redmagic_device_result.json`

## Pass Condition

The bounded RedMagic lane is `PASS` only when:

- ADB reaches the device,
- Termux is present on the device,
- the foreground session shows the canonical packet path under `/storage/emulated/0/Download/`,
- the visible device-side SHA-256 matches the Mac-side packet hash `d428f395c3979cac8a967e8a014649c0220c37ba850a8da0aee2756d0b9393c7`,
- and the artifact note states clearly what remains unproven.

## Explicit Non-Claims

- This runbook does not prove headless on-device Python or bundle regeneration.
- This runbook does not prove ROS2 parity, certification, or broader device-native replay closure.
- This runbook does not authorize or use RunPod.
