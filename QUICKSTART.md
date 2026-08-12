# Quickstart (10 Commands)

Run these in order for a normal day-to-day session.

```bash
cd /Users/jason.yates/go2_webrtc_control
source .venv/bin/activate
python3 -m go2_control.cli stand-up
python3 -m go2_control.cli stop
python3 -m go2_control.cli routine short-walk
python3 -m go2_control.cli sit
cd go2_control
python3 -m http.server 8000
curl -I http://localhost:8000/move_simulation.html | head -n 1
open http://localhost:8000/move_simulation.html
```

Notes:

- Leave the server terminal running while using the simulator.
- After editing routine files, refresh the browser page to reload steps.

---

## VR bridge startup (Quest 3S)

Run these after the normal session above when you want Quest control.

```bash
# 1. Find your Mac's IP on the shared network
ipconfig getifaddr en0

# 2. Start the VR bridge (keep this terminal open)
python3 -m go2_control.vr_bridge

# 3. In a second terminal — verify the bridge is up
curl http://localhost:8765/health

# 4. On your Quest 3S, open the browser and go to:
#    http://<YOUR_MAC_IP>:8765/vr/index.html
#    Tap Connect Control → Connect Camera → Enter VR
```

Tips:

- Mac and Quest must be on the same Wi-Fi network.
- Hold the **left trigger** while steering — releasing it stops the robot within 250 ms (deadman switch).
- If the bridge fails to start, re-run `python3 -m pip install fastapi uvicorn aiortc av` then retry.
