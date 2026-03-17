# Gate RedMagic Runbook: ADB Validation

## Objective

Capture the exact RedMagic device validation state and determine whether the current Android path is executable or blocked.

## Commands

1. `adb devices -l`
2. `adb shell getprop ro.product.model`
3. `adb shell getprop ro.product.cpu.abi`
4. `adb shell pm list packages | rg termux`
5. `adb shell am start -n com.termux/.app.TermuxActivity`
6. `adb shell '/data/data/com.termux/files/usr/bin/python3 -V'`
7. `adb shell '/data/data/com.termux/files/usr/bin/pkg --version'`
8. `adb shell input text pwd`
9. `adb shell input keyevent KEYCODE_ENTER`
10. `adb exec-out screencap -p > proofs/reruns/robotics_phase3_local_2026-03-17/redmagic_termux_pwd_execution.png`
11. `adb shell input text pkg`
12. `adb shell input keyevent KEYCODE_ENTER`
13. `adb exec-out screencap -p > proofs/reruns/robotics_phase3_local_2026-03-17/redmagic_termux_pkg_usage.png`

## Expected Output

- `proofs/reruns/robotics_phase3_local_2026-03-17/redmagic_adb_validation.json`
- `proofs/reruns/robotics_phase3_local_2026-03-17/redmagic_termux_pwd_execution.png`
- `proofs/reruns/robotics_phase3_local_2026-03-17/redmagic_termux_pkg_usage.png`

## Pass Condition

The device lane is `PASS` only when:

- ADB reaches the device,
- the device reports an ARM64 ABI,
- Termux is installed,
- and either:
  - a callable Python or package-management path can be executed from the current external command surface, or
  - an ADB-driven foreground Termux session executes a real command and the result is preserved in screenshot-backed evidence.

## Blocked Condition

The device lane is `BLOCKED` when:

- direct private-path execution remains inaccessible, and
- no foreground Termux execution path can be proven through durable evidence.

## Scope Guard

- Device attachment alone does not count as parity success.
- Screenshot-backed foreground execution proves a real on-device command surface, not ROS2 parity closure.
- This runbook captures current physical follow-through truth. It does not replace hosted GitHub Actions evidence.
