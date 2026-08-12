# Go2 WebRTC Control Walkthrough

This guide walks you through the full workflow:

1. Set up environment
2. Run safe robot commands
3. Use teleop
4. Use the movement simulator
5. Keep simulator data synced with Python edits
6. Troubleshoot common issues

## 1) One-time setup

From the project root, create and activate your virtual environment if needed:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -U pip
python3 -m pip install go2-webrtc-connect pynput
```

Optional: install this package in editable mode:

```bash
python3 -m pip install -e .
```

## 2) Basic robot control (safe commands)

Run from project root while connected to your Go2 LocalAP network.

Quick checks:

```bash
python3 -m go2_control.cli stand-up
python3 -m go2_control.cli stop
python3 -m go2_control.cli sit
```

Run a short safe walk:

```bash
python3 -m go2_control.cli walk-for --forward 0.1 --duration 2.0
```

Run preset routines:

```bash
python3 -m go2_control.cli routine greet
python3 -m go2_control.cli routine short-walk
```

Open the menu UI in terminal:

```bash
python3 -m go2_control.cli menu
```

## 3) Global keyboard teleop

Start teleop:

```bash
python3 -m go2_control.pynput_teleop
```

Key mapping:

- W: forward
- S: backward
- A: turn left
- D: turn right
- Space: stop
- Q: sit and quit

On macOS, if keys do not work globally, enable Input Monitoring and Accessibility permissions for your terminal app in System Settings.

## 4) Run the simulator

The simulator is in [go2_control/move_simulation.html](go2_control/move_simulation.html).

Start a local web server from the folder that contains the simulator file:

```bash
cd go2_control
python3 -m http.server 8000
```

Open:

- http://localhost:8000/move_simulation.html

If you serve from project root instead, open:

- http://localhost:8000/go2_control/move_simulation.html

## 5) Auto-load behavior (important)

The simulator tries to read routine data from Python files every page load.

Files parsed by the simulator include:

- [go2_control/demo.py](go2_control/demo.py)
- [go2_control/stand_wag_sit_example.py](go2_control/stand_wag_sit_example.py)
- [go2_control/repeat_tilt_sit.py](go2_control/repeat_tilt_sit.py)
- [go2_control/square_walk_sit.py](go2_control/square_walk_sit.py)
- [go2_control/walk_turn_walk_sit.py](go2_control/walk_turn_walk_sit.py)
- [go2_control/performance_routine.py](go2_control/performance_routine.py)
- [go2_control/pynput_teleop.py](go2_control/pynput_teleop.py)
- [go2_control/cli.py](go2_control/cli.py)

Workflow after editing routines:

1. Save your Python file.
2. Refresh the simulator page.
3. Confirm the subtitle indicates routines were auto-loaded.

If parsing fails, simulator falls back to built-in sample steps so the page still works.

## 6) Troubleshooting

### ERR_CONNECTION_REFUSED on localhost

Cause: server not running on that port/folder.

Fix:

```bash
cd go2_control
python3 -m http.server 8000
```

Then test quickly:

```bash
curl -I http://localhost:8000/move_simulation.html
```

Expected: HTTP 200.

### python command not found

Use python3 instead:

```bash
python3 -m http.server 8000
```

### Relative import error when running a script directly

If you see attempted relative import with no known parent package, run with module form from project root:

```bash
python3 -m go2_control.demo
```

### Teleop keys not detected on macOS

Grant terminal Input Monitoring and Accessibility permissions.

### Robot safety reminders

- Keep walk speed at or below 0.3 m/s.
- Avoid acrobatic sport API IDs 1025, 1026, 1027.
- Keep clear physical space around the robot during tests.

## 7) Recommended daily workflow

1. Connect Mac to Go2 LocalAP.
2. Activate environment.
3. Run a short CLI safety check.
4. Edit routine Python files.
5. Refresh simulator to validate motion sequence visually.
6. Run on hardware only after simulator and code review look correct.

## 8) Quest 3S VR bridge

The VR bridge streams a control WebSocket and optional camera feed to your Meta Quest 3S browser.

### Install VR dependencies (one-time)

```bash
source .venv/bin/activate
python3 -m pip install fastapi uvicorn aiortc av pydantic
```

Or install the whole project with VR extras:

```bash
python3 -m pip install -e ".[vr]"
```

### Find your Mac's local IP

The Quest browser needs your Mac's IP on the shared Wi-Fi network (not localhost):

```bash
ipconfig getifaddr en0
```

If on a wired or alternate interface try `en1`. Note the IP (e.g. `192.168.1.50`).

### Start the bridge

```bash
python3 -m go2_control.vr_bridge
```

Expected console output:

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8765
```

Verify it is alive:

```bash
curl http://localhost:8765/health
```

Expected: `{"status":"ok"}`

### Open the control page on your Quest

1. Put on your Quest 3S.
2. Open the Quest Browser.
3. Navigate to:

```
http://<YOUR_MAC_IP>:8765/vr/index.html
```

Replace `<YOUR_MAC_IP>` with the address from the step above.

### Connect and control

| Step | Button on page | Result |
|------|---------------|--------|
| 1 | **Connect Control** | Opens WebSocket to bridge |
| 2 | **Connect Camera** | Starts WebRTC video from Go2 |
| 3 | **Enter VR** | Launches immersive WebXR view |

### Quest controller mapping

| Input | Action |
|-------|--------|
| Left thumbstick Y-axis | Forward / backward |
| Right thumbstick X-axis | Turn left / right |
| Left trigger (hold) | Deadman — releases E-stop |
| A button | Stand up |
| B button | Sit |
| Right thumbstick click | Emergency stop |

### Keyboard fallback (browser on Mac)

| Key | Action |
|-----|--------|
| W / S | Forward / backward |
| A / D | Turn left / right |
| Space | Stop |

### Deadman safety note

The bridge requires the **left trigger to be held** while sending move commands. Releasing it sends an immediate stop within 250 ms. This prevents runaway motion if the Quest loses tracking or the page freezes.
