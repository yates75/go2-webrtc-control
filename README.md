# Go2 WebRTC Control

Small async helper code for a Unitree Go2 Pro connected over the robot's WiFi hotspot using `go2-webrtc-connect`.

## What it does

- Wraps the `rt/api/sport/request` JSON framing
- Provides convenience methods for common sport commands
- Keeps the move speed capped at `0.3 m/s` for the Lion Cub shell
- Avoids acrobatic commands by design

## Files

- `go2_control/client.py` contains the reusable helper class
- `go2_control/config.py` loads the robot settings from TOML
- `go2_control/cli.py` contains the command-line control entry point
- `go2_control/demo.py` contains a small example control script
- `go2_control/camera_view.py` saves snapshots or shows a live preview of the front camera
- `go2_control/lidar_view.py` prints and optionally records decoded LIDAR point-cloud messages
- `go2_control/telemetry.py` reads battery, orientation, velocity, and odometry (read-only)
- `go2_control/audio.py` lists and plays built-in sounds through the onboard speaker
- `go2_control/remote_input.py` reads live input from a paired physical controller (read-only)
- `go2_control/experimental.py` controls LED color/volume/brightness and obstacle avoidance (sourced command IDs); SLAM-mapping start is a documented stub, plus safe read-only SLAM topic watching
- `go2_control/block_ide.html` / `block_ide.js` is a drag-and-drop Blockly editor that generates real Python for this project's API (serve with `python -m http.server`, no robot connection from the browser)
- `go2_control/object_tracker.py` detects and logs a moving object's position from the camera feed using a pretrained YOLO model (passive only, optional `ultralytics`/`opencv-python` dependency)
- `go2_control/lidar_tracker.py` detects and logs a moving object's position using the LIDAR feed (background-subtraction + voxel clustering, passive only)
- `go2_control/follow.py` actively turns/walks the robot to follow a detected object -- the first script where movement is driven by a live model, not fixed commands; heavy safety guardrails (see its docstring)
- `go2_control/dataset_capture.py` / `train_classifier.py` / `recognize.py` capture your own labeled images, fine-tune a small classifier on them, and run it live (genuine supervised ML training)
- `go2_control/record_demo.py` / `train_follow_policy.py` record (object position -> human action) demonstrations and fit a small transparent linear policy from them; load it into `follow.py` with `--policy` to compare a trained behavior against the hand-coded controller
- `go2_config.toml` is the editable config file for your defaults
- `ROBOT_MOVEMENT_VISUALS.md` shows movement flow diagrams for each program
- `WALKTHROUGH.md` is a full setup and usage guide for robot control and simulation
- `QUICKSTART.md` is a 10-command day-to-day run sheet
- `STUDENT_TUTORIAL.md` is a teaching-ready walkthrough covering movement, camera, and LIDAR
- `CHATGPT_WORKBOOK_PROMPT.md` is a ready-to-paste ChatGPT prompt for generating a Stage 5/6 student workbook covering every capability in this project

## Run

Install the dependency in your Python environment, then run:

```bash
python -m go2_control.cli stand-up
python -m go2_control.cli walk-for --forward 0.1 --duration 2.0
python -m go2_control.cli routine greet
python -m go2_control.cli menu
python -m go2_control.demo
```

## Global key teleop

This project uses `pynput` for keyboard control without needing the terminal window in focus.

Install it with pip:

```bash
python -m pip install pynput
```

On macOS, you may also need to allow the terminal or Python app in System Settings so `pynput` can monitor global keyboard input.

## Move simulation

Use the simulator page to preview how each program moves the robot without connecting to hardware.

1. Start a simple local server from the project root:

```bash
python -m http.server 8000
```

2. Open this URL in a browser:

```text
http://localhost:8000/go2_control/move_simulation.html
```

The simulator auto-loads step data from the Python files each time the page is refreshed, then animates path, heading, tilt, wag, and sit/stand transitions.

## Preset routines

- `greet` balances, waves, shows content, then stops
- `calm-start` lowers speed, balances, stands, then stops
- `short-walk` balances, walks briefly at the configured default speed, then stops
- `reset` stops motion, returns to balance stand, then stops again
- `turn-left` balances, then performs a slow left turn
- `turn-right` balances, then performs a slow right turn
- `back-up-slowly` balances, then backs up at a conservative speed

## Environment variables

These override the TOML config without editing files:

- `GO2_ROBOT_IP`
- `GO2_WIFI_NAME`
- `GO2_DEFAULT_WALK_SPEED_MPS`

## Notes

- The code uses `asyncio` throughout.
- Replace the connection details in the demo with the values that match your setup.
- The example only sends safe commands and keeps walking speed conservative.
- For shell safety, the helper caps walk speed at `0.3 m/s` and blocks acrobatic commands.
- Edit [go2_config.toml](/Users/jason.yates/go2_webrtc_control/go2_config.toml) to change your robot IP, WiFi name, and default walk speed.
