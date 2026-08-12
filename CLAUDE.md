# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Python toolkit for controlling a Unitree Go2 Pro robot over WebRTC (movement, camera, LIDAR, telemetry, audio, and ML-based object tracking), connecting over the robot's own WiFi hotspot (LocalAP mode). Built for a student robotics course — see `STUDENT_TUTORIAL.md` for the full curriculum and `README.md` for the per-file feature list.

## Commands

Dev install (editable, resolves the vendored driver via the `file:` dependency below):
```bash
pip install -e .
pip install -e ".[tracking]"   # adds ultralytics/opencv-python/lap for object_tracker.py etc.
```

Run any tool: most scripts have no console entry point and are invoked as modules:
```bash
python -m go2_control.cli walk-for --forward 0.1 --duration 2.0
python -m go2_control.camera_view --live
python -m go2_control.telemetry state --count 5
```
Only these five have registered console scripts (`[project.scripts]` in `pyproject.toml`): `go2-control`, `go2-demo`, `go2-teleop`, `go2-vr-bridge`, `go2-object-tracker`.

**There is no automated test suite** (no pytest/unittest). "Testing" means running a script against the real, powered-on robot and a human visually confirming what happened — that's what the `verify_*.sh` scripts at the repo root do (e.g. `./verify_sensors.sh`, `./verify_movement_stage1.sh`). They require being connected to the robot's WiFi hotspot. Treat any change to `go2_webrtc_driver` protocol handling, `client.py` command construction, or connection/timing logic as unverified until one of these has actually been run against hardware — static analysis alone won't catch protocol-level breakage here.

No lint/format tooling is configured for this package (no ruff/black/mypy config at the repo root).

### Building the redistributable student bundle

`pyproject.toml`'s dependency on the vendored driver uses a local `file:` path, which only resolves on this dev machine — it must NOT end up in a wheel meant for other computers. To rebuild `dist_bundle/`:
```bash
python -m build --wheel --outdir dist_bundle vendor/go2_webrtc_connect   # standalone, no special handling needed
```
For the main package, temporarily edit the `go2-webrtc-connect` line in `dependencies` (in `pyproject.toml`) to drop the `@ file:./vendor/go2_webrtc_connect` suffix, build, then restore it exactly:
```bash
# edit pyproject.toml: "go2-webrtc-connect @ file:./vendor/go2_webrtc_connect" -> "go2-webrtc-connect"
rm -rf build go2_webrtc_control.egg-info   # stale build/lib cache silently reuses old file lists otherwise
python -m build --wheel --outdir dist_bundle .
# edit pyproject.toml back to the file: pin
rm -rf build go2_webrtc_control.egg-info
```
Verify by installing both wheels into a throwaway venv from a directory with no local `go2_control/` folder on disk (otherwise Python silently resolves the package from the cwd instead of site-packages, and the test proves nothing).

## Architecture

**Two-package structure.** `go2_control/` (this project's own code) depends on `go2-webrtc-connect` (the underlying WebRTC/driver library), which is *not* the unpatched PyPI release — it's a vendored, patched fork at `vendor/go2_webrtc_connect/` with its own `pyproject.toml`, pinned via `file:./vendor/go2_webrtc_connect` in the main `dependencies` list. The patch (in `unitree_auth.py`) adds AES-GCM decryption of the `con_notify` handshake payload for Go2 firmware ≥1.1.8 (signaled by `data2: 2` in the response) — without it, the SDP handshake fails with "RSA key format is not supported" on any robot running that firmware or newer. Don't "fix" imports by pointing back at plain `go2-webrtc-connect` from PyPI.

**Connection pattern.** Almost every script independently does `Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)` → `connect()` → do one thing → `disconnect()`; there's no shared/pooled connection. `client.py`'s `Go2ControlClient` is a higher-level wrapper (used by `cli.py`) that centralizes sport-command construction and safety caps (`MAX_SAFE_WALK_SPEED_MPS = 0.3`, `SAFE_ACROBATIC_API_IDS` blocklist) — don't loosen these without being explicitly asked, they're a deliberate hardware-safety constraint ("Lion Cub shell"), not an arbitrary default. Many leaf scripts (`camera_view.py`, `lidar_view.py`, `telemetry.py`, `audio.py`, the standalone `*_sit.py` demo scripts) talk to `go2_webrtc_driver` directly rather than going through `client.py`.

**Protocol gotchas that look like bugs but aren't (or are, but not where you'd expect):**
- Any subscription to a high-frequency state topic (`rt/sportmodestate`, `rt/wirelesscontroller`, SLAM topics) silently receives nothing forever unless `conn.datachannel.disableTrafficSaving(True)` is called first. Scripts that read state (`telemetry.py`, `remote_input.py`, `experimental.py`'s `watch_slam_topics`) must call this before subscribing.
- The sport-state topic name varies by firmware: subscribe to *both* `RTC_TOPIC["SPORT_MOD_STATE"]` (`rt/sportmodestate`) and `RTC_TOPIC["LF_SPORT_MOD_STATE"]` (`rt/lf/sportmodestate`) — which one actually fires depends on the robot.
- After `StandUp`, wait ~2 seconds before sending `Move` — 1 second is empirically not enough settle time and `Move` will silently no-op (accepted with `status.code: 0`, robot leans but never steps).
- **Known unresolved limitation**: even with correct timing/command shape, `Move` (API 1008) is intermittently unreliable on the currently-tested robot's `mcf` motion-service firmware — same code, same commands, same timing sometimes walks and sometimes doesn't. Extensively diagnosed (mode-switching, obstacle avoidance, no-reply vs request/response send patterns, physical-remote comparison all ruled out as the cause). This is a robot/firmware-side issue, not something to keep re-debugging in code — see the "Known issues" style notes in `STUDENT_TUTORIAL.md` Part 3/13 for the equivalent LIDAR-schema caveat pattern.

**Connecting to the robot means no internet.** LocalAP mode requires being on the robot's own WiFi hotspot, which doesn't route to the internet. Anything requiring a fresh download (pip installs, the YOLO weights, the `lap` package for `object_tracker.py --live`) must happen on normal WiFi *before* switching networks to test against hardware.

**Config resolution.** `go2_control/config.py`'s `DEFAULT_CONFIG_PATH` resolves `go2_config.toml` relative to the current working directory (not the installed package location) — this is intentional so a config file dropped next to wherever the tool is run from gets picked up, including from an installed wheel where there is no source tree to resolve against.

**`diagnostics/`** holds standalone one-off troubleshooting scripts from initial hardware bring-up (connection handshake, motion-mode, obstacle-avoidance probes). They're excluded from the installable package on purpose (not curriculum material) but kept for future hardware debugging — they use absolute imports (`from go2_control.client import ...`) since they live outside the `go2_control` package.
