# Go2 WebRTC Control — Student Tutorial

A hands-on tutorial for driving the Unitree Go2 Pro, viewing its camera feed, and viewing/recording its LIDAR feed with Python.

**Read this first:** this robot is a real physical machine. Always work in a clear, open space, keep hands and feet away from the legs while it moves, and never run a command you don't understand yet. Every movement command in this project is speed-limited to keep things safe — don't remove those limits.

---

## For teachers: mapping to the NSW Stage 5/6 Computing syllabuses

Every part below ends with a **Classroom activities** block, tagged against real focus areas/modules from the current NESA syllabuses, so activities can be lifted straight into a program or assessment without re-deriving the links yourself.

| Tag | Course | Year | Focus area / module |
|---|---|---|---|
| `CT-Mech` | Computing Technology 7–10 | Stage 5 | Building mechatronic and automated systems |
| `CT-Data` | Computing Technology 7–10 | Stage 5 | Analysing data |
| `CT-UX` | Computing Technology 7–10 | Stage 5 | Designing for user experience |
| `CT-Net` | Computing Technology 7–10 | Stage 5 | Modelling networks and social connections |
| `CT-Apps` | Computing Technology 7–10 | Stage 5 | Developing apps and web software |
| `CT-Games` | Computing Technology 7–10 | Stage 5 | Creating games and simulations |
| `SE-Fund` | Software Engineering 11–12 | Year 11 | Programming fundamentals |
| `SE-OOP` | Software Engineering 11–12 | Year 11 | The object-oriented paradigm |
| `SE-Mech` | Software Engineering 11–12 | Year 11 | Programming mechatronics |
| `SE-Secure` | Software Engineering 11–12 | Year 12 | Secure software architecture |
| `SE-Web` | Software Engineering 11–12 | Year 12 | Programming for the web |
| `SE-Auto` | Software Engineering 11–12 | Year 12 | Software automation |
| `SE-Proj` | Software Engineering 11–12 | Year 12 | Software Engineering project |
| `EC-Media` | Enterprise Computing 11–12 | Year 11 | Interactive media and the user experience |
| `EC-Net` | Enterprise Computing 11–12 | Year 11 | Networking systems and social computing |
| `EC-Cyber` | Enterprise Computing 11–12 | Year 11 | Principles of cybersecurity |
| `EC-DataSci` | Enterprise Computing 11–12 | Year 12 | Data science |
| `EC-DataViz` | Enterprise Computing 11–12 | Year 12 | Data visualisation |
| `EC-Intel` | Enterprise Computing 11–12 | Year 12 | Intelligent systems |
| `EC-Proj` | Enterprise Computing 11–12 | Year 12 | Enterprise project |

This project's architecture happens to line up well with the mechatronics/automation throughline shared by all three courses: a physical machine (mechatronics) driven by software commands (programming), watched over by sensors and safety layers (automation, systems thinking), and increasingly handed autonomy through models trained on real data (intelligent systems) — with every step of that progression staged behind explicit, discussed safety caps. That progression is itself a live case study for `SE-Secure`/`EC-Cyber`'s emphasis on designing safety and trust boundaries into a system from the start, rather than bolting them on afterward.

A **capstone project ideas** section sized for each course's end-of-year project (`SE-Proj`, `EC-Proj`, or a Stage 5 combined-focus-area project) is at the end of this document, after Part 17.

---

## Part 0 — One-time setup

1. Unzip the folder you were given, and open a terminal inside it.

2. Run the installer once (this creates a `.venv` folder here and installs everything needed — safe to run again later, it'll just reuse the existing one):

    ```bash
    ./install_mac.sh
    ```

3. Activate the virtual environment (do this every time you open a new terminal in this folder):

    ```bash
    source .venv/bin/activate
    ```

4. Power on the Go2 and wait for it to fully boot (listen for it to finish its startup sound/stand cycle).

5. Connect your laptop's WiFi to the robot's hotspot (check with your teacher for the exact network name — it may not be the default `UNITREE_GO2`).

6. Check the connection:

    ```bash
    ping 192.168.12.1
    ```

    You should see replies. If not, re-check the WiFi connection before continuing — nothing below will work without this.

    **One thing to know:** while connected to the robot's WiFi, your laptop has no internet access (the robot's hotspot doesn't route to the internet). That's fine for everything in this tutorial except the one-time setup itself and Part 12+'s first-run model download — do those while on your normal WiFi first, *then* switch to the robot's network.


**New to Python, or teaching students who are?** Consider starting with **Part 11 — Block-based programming** at the end of this tutorial before Parts 1–10. It's a drag-and-drop block editor covering every capability below, with the real Python code shown live as you build — a gentler on-ramp that still teaches the actual API.

---

## Part 1 — Basic movement commands

### 1a. Try it from the command line (no coding required)

```bash
python -m go2_control.cli stand-up
python -m go2_control.cli sit
python -m go2_control.cli walk-for --forward 0.1 --duration 2.0
python -m go2_control.cli menu          # interactive menu, good for first-time exploring
```

### 1b. Try it in Python

This is the pattern every control script in this project follows: **connect → send commands → disconnect**.

```python
import asyncio
from go2_control.client import Go2ControlClient

async def main():
    client = Go2ControlClient()
    await client.connect()
    try:
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(1.0)
        await client.walk_for(0.1, duration_s=2.0)   # forward at 0.1 m/s for 2 seconds
        await client.sit()
    finally:
        await client.disconnect()

asyncio.run(main())
```

Save this as your own file (e.g. `my_first_walk.py`) and run it with:

```bash
python my_first_walk.py
```

**Useful movement methods on `client`:**

| Method | What it does |
|---|---|
| balance_stand() | Stand and hold balance |
| stand_up() / stand_down() | Stand up / lower down |
| sit() / rise_sit() | Sit / stand up from sitting |
| stop_move() | Stop all motion immediately |
| move(forward_mps, sideways_mps, turn_rps) | Send one movement command |
| walk_for(forward_mps, duration_s, ...) | Walk for a set time, then auto-stop |
| hello(), content(), stretch(), heart_pose() | Fun gesture commands |

**Safety rails already built in** ([client.py](go2_control/client.py)):

- Forward/sideways speed can't exceed **0.3 m/s**.
- Turn rate can't exceed **1.0 rps**.
- Acrobatic commands (flips etc.) are blocked outright.

### 1c. Preview a routine before running it on hardware

You can visualize any movement sequence in a browser first:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/go2_control/move_simulation.html` — it auto-reads step data from the project's Python files and animates the path.

### 1d. Try a preset routine

```bash
python -m go2_control.cli routine greet
python -m go2_control.cli routine short-walk
python -m go2_control.cli routine turn-left
```

Full list: `greet`, `calm-start`, `short-walk`, `reset`, `turn-left`, `turn-right`, `back-up-slowly`, `handoff`.

**`reset` vs `handoff`:** `reset` only clears *motion* (stops, then stands neutrally) — it doesn't touch other sticky settings a script might have changed. `handoff` is the one to run before giving the robot to a student to drive with the official app or physical remote:

```bash
python -m go2_control.cli routine handoff
```

It turns off manual pose mode, re-enables obstacle avoidance, resets body height, foot-raise height, and speed level to their defaults, then stands neutrally — and because the CLI always disconnects when it finishes, running this from a terminal also releases your script's connection, which is the other half of actually handing over control. **What it deliberately doesn't touch:** gait selection (`switch_gait`, Part 4) — there's no confirmed default gait ID for this firmware to switch back to, so if you changed it, either remember what you set or power-cycle the robot if you're not sure.

**Exercise for students:** open [cli.py](go2_control/cli.py) and find `run_routine()`. Add a new routine name (e.g. `"figure-eight"`) that chains a left turn and a right turn together, using only the safe methods above.

### Classroom activities (Stage 5/6 Computing)

- **`CT-Mech`** Trace `MAX_SAFE_WALK_SPEED_MPS` from where it's defined in `client.py` through to where it's enforced, and write a short paragraph on why a hard-coded software limit counts as a genuine safety component of a mechatronic system, not just a suggestion.
- **`SE-Fund`** Before touching code, write the `walk_for()` behaviour ("walk at this speed, then stop after this many seconds") as pseudocode or a flowchart. Compare your version to what `client.py` actually does — where did you under- or over-specify the algorithm?
- **`SE-Mech`** The browser simulator (1c) only ever shows *intended* motion. Write a short prediction of at least two reasons the robot's real executed path might differ from the simulation (e.g. actuator response time, surface grip, firmware timing) — you'll get to check this prediction for real in Part 6.
- **`EC-Net`** Diagram the connect → send commands → disconnect pattern as a sequence diagram (laptop, WiFi, robot). Annotate what happens to the robot if the WiFi connection drops in the middle of a `walk_for()` call — a first look at reliability in networked control systems.
- **`SE-Proj`/`EC-Proj`** Before implementing the `"figure-eight"` routine exercise above, write two or three acceptance criteria for it first (e.g. "ends facing the same direction it started," "never exceeds the speed caps"). Implement against your own criteria, then check them off.

---

## Part 2 — Viewing the camera feed

The camera is exposed through [camera_view.py](go2_control/camera_view.py).

### 2a. Save snapshots (works out of the box)

```bash
python -m go2_control.camera_view --count 10 --interval 1.0
```

This connects, saves 10 JPEGs one second apart into `./camera_snapshots/`, then disconnects. Open the folder afterward and look at the images.

### 2b. Live preview window (optional, needs one extra package)

```bash
pip install opencv-python
python -m go2_control.camera_view --live
```

A window pops up showing the live feed. Press `q` to close it early.

### 2c. How it works (for students who want to go deeper)

```python
conn.video.add_track_callback(my_callback)   # register FIRST
conn.video.switchVideoChannel(True)          # THEN switch the feed on
```

The Go2 only starts sending video frames once the channel is switched on — if you switch it on before registering your callback, the first frame gets consumed internally and your callback never fires. This order matters.

**Exercise for students:** modify `camera_view.py` so it saves a snapshot only when a keyboard key is pressed, instead of on a fixed timer (hint: combine with `pynput`, already used in [pynput_teleop.py](go2_control/pynput_teleop.py)).

### Classroom activities (Stage 5/6 Computing)

- **`CT-UX`** Sketch or wireframe an on-screen status flow for a non-technical operator using the snapshot tool: what should appear when a photo is taken, when the connection drops, when the folder fills up? Redesign 2a's console output to match your wireframe.
- **`EC-Media`** Compare the timer-driven capture in 2a against the keyboard-triggered capture from the exercise above as two different interactive-media capture models. Write a short recommendation on when each is the right choice (unattended monitoring vs. a human deciding the moment).
- **`SE-Fund`** Explain, in your own words, why `add_track_callback` must be registered before `switchVideoChannel(True)`. Turn it into a general rule about event-driven programming (register handlers before triggering the event source), and find or invent one other example of the same class of bug.
- **`CT-Mech`** The camera is one sensor this robot exposes. As you work through the rest of this tutorial, keep a running list of every other sensor (LIDAR, telemetry, remote input, audio) and classify each as "read-only monitoring," "used to trigger automation," or both.

---

## Part 3 — Viewing and recording the LIDAR feed

The LIDAR feed is exposed through [lidar_view.py](go2_control/lidar_view.py).

### 3a. View live LIDAR messages

```bash
python -m go2_control.lidar_view --count 20
```

This turns the LIDAR sensor on, subscribes to its point-cloud topic, and prints the structure of each incoming message (field names, or the raw data type if it isn't a dictionary) so you can see exactly what the sensor returns.

### 3b. Record a LIDAR session to disk

```bash
python -m go2_control.lidar_view --record --out-dir lidar_recording --count 50
```

Each decoded frame is saved as `lidar_recording/frame_0000.pkl`, `frame_0001.pkl`, etc. To load one back later for analysis:

```python
import pickle

with open("lidar_recording/frame_0000.pkl", "rb") as f:
    frame = pickle.load(f)

print(type(frame))
if isinstance(frame, dict):
    print(frame.keys())
```

### 3c. What the LIDAR payload actually contains (confirmed against real hardware)

Each frame is a dict with five keys: `point_count`, `face_count`, `positions`, `uvs`, `indices`. `positions`/`uvs`/`indices` are **flat mesh vertex-buffer arrays** — the same shape of data you'd feed to a 3D graphics renderer (position, texture coordinate, and triangle-index arrays), not a plain list of `(x, y, z)` points. That's consistent with the decoder's name, `libvoxel` — it's building a triangulated surface mesh out of the voxel grid, not just returning raw points.

To turn `positions` into individual 3D points:

```python
positions = frame["positions"].reshape(-1, 3)   # each row is one (x, y, z)
print(positions.shape)
print(positions[:5])
```

**Important:** `positions` is `dtype=uint8` with values roughly in the 0–255 range — these are **integer voxel-grid indices**, not meters. To get real-world distances, multiply by the actual voxel size used during decoding (see `--voxel-size` in [lidar_tracker.py](go2_control/lidar_tracker.py), default `0.1` meters per voxel) and account for whatever origin offset the grid uses. Treating these numbers as metric coordinates directly will give you wrong distances.

**Exercise for students:** load a recorded frame, reshape `positions`, and plot a 2D top-down scatter of `x` vs `y` (e.g. with `matplotlib`). Compare the shape you see to the room you recorded in.

**Exercise for students:** after running 3a once and seeing the real field names, write a small script that loads a recorded `.pkl` frame and prints summary statistics (e.g. number of points, or min/max coordinate ranges) using those actual field names.

### 3d. Visualize a recorded frame

[visualize_lidar.py](visualize_lidar.py) (repo root, not part of the `go2_control` package) does the plotting from the two exercises above for you — it loads a `.pkl` frame from 3b, reshapes and scales `positions` by `--voxel-size` the same way 3c describes, and plots it. It needs `matplotlib` and `numpy`, which aren't part of this project's normal install (`pip install matplotlib numpy` if you don't already have them) — run this on normal WiFi, before switching to the robot's hotspot.

```bash
python visualize_lidar.py lidar_recording/frame_0000.pkl          # 3D scatter, opens a window
python visualize_lidar.py lidar_recording/frame_0000.pkl --2d     # top-down 2D view instead
python visualize_lidar.py lidar_recording/frame_0000.pkl --out frame.png   # save a PNG instead of opening a window
```

It prints the point count and the x/y/z extent in meters before plotting, so you can sanity-check the numbers against 3c's voxel-size caveat before trusting the picture.

### Classroom activities (Stage 5/6 Computing)

- **`SE-Mech`/`CT-Mech`** Derive, on paper, the formula for turning a voxel index into a real-world distance given an origin offset. Test it by physically measuring a real distance in the room with a tape measure and comparing it to what your formula predicts from a recorded frame.
- **`EC-DataViz`** Use `visualize_lidar.py` to compare the 2D and 3D views of the same frame. Write a short note on what information the 2D top-down view discards, and describe a real scenario where that tradeoff would (and wouldn't) be acceptable in a dashboard built for a non-technical audience.
- **`CT-Data`/`EC-DataSci`** Record several frames and write a script that plots point count across them. Discuss what a sudden drop or spike would suggest about sensor health, and why you'd want a check like this running *before* trusting the sensor for automated decisions later (Part 13, Part 14).
- **`SE-Secure`/`EC-Cyber`** Reverse-engineering an undocumented sensor payload format (3c) is itself a security-adjacent skill. Discuss, with reference to this exact situation, the difference between reverse-engineering a closed protocol for interoperability/education versus for malicious purposes — and where the line actually sits.

---

## Part 4 — More gestures and gait tuning

New methods on `Go2ControlClient` ([client.py](go2_control/client.py)), all using documented sport-command IDs, all zero-risk (no acrobatics):

```python
await client.dance1()             # built-in dance routine 1
await client.dance2()             # built-in dance routine 2
await client.wallow()             # roll/shake gesture
await client.scrape()             # paw scrape gesture
await client.wiggle_hips()        # hip wiggle gesture
await client.content()            # fixed in this update — now sends the real "Content" command, not Dance1
```

Gait/posture tuning (single-value commands, same shape as `speed_level()`):

```python
await client.switch_gait(0)               # select a gait pattern (valid IDs are firmware-dependent)
await client.set_body_height(0.0)         # adjust standing height, relative offset in meters
await client.set_foot_raise_height(0.0)   # adjust foot swing height while walking
await client.pose(True)                   # enable manual pose mode; False to release it
```

**A bug worth showing the class:** the previous version of `content()` actually sent the `Dance1` command (id 1022) instead of the real `Content` command (id 1020) — the id was copy-pasted wrong. It's a good real-world example of why you should always trace a "magic number" ID back to its source (`go2_webrtc_driver/constants.py`'s `SPORT_CMD` dict) instead of trusting a method name.

**Exercise for students:** write a short routine that calls `switch_gait`, waits, calls `walk_for(0.1, duration_s=2.0)`, and compares how the walk feels across two different gait IDs. Discuss why some experiments here (unlike everything above) require you to already know a valid ID for your firmware — where would you look that up safely?

### Classroom activities (Stage 5/6 Computing)

- **`SE-Fund`/`SE-OOP`** Using the `content()` bug as your starting point, find `SPORT_CMD` in `constants.py` and design a small validation function or class that raises a clear error if an unknown or unmapped command ID is used. Discuss why explicit validation matters more in mechatronic command dispatch than in, say, a script that only prints text.
- **`CT-Mech`** Test `set_body_height` and `set_foot_raise_height` on two different surfaces at school (e.g. carpet vs. tile). Compare how the robot copes, and connect your observations to how real quadruped mechatronics adapts posture and gait to terrain.
- **`SE-Mech`** On paper, design a state machine for gait transitions: standing → walking → switching gait, including guard conditions like the "wait ~2 seconds after StandUp before Move" rule documented in this project's `CLAUDE.md`. Discuss why a state machine, not a straight-line script, is the right model here.
- **`SE-Auto`** Chain `switch_gait`, `walk_for`, and (once you've reached Part 5) telemetry logging into a small automated "gait comparison" test harness: run each candidate gait for a fixed distance, log the result, and report which performed best against a metric you define. This is a first hands-on software-automation testing exercise.

---

## Part 5 — Telemetry: battery, orientation, and velocity

New module: [telemetry.py](go2_control/telemetry.py). This only **reads** data the robot is already broadcasting — no commands are sent, so it's safe to run any time, even mid-walk.

```bash
python -m go2_control.telemetry state --count 20
```

Example output line: `battery=87%, position=[...], velocity=[...], roll_pitch_yaw=[...]`.

In Python:

```python
import asyncio
from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_control.telemetry import stream_state

async def main():
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await stream_state(conn, count=10)
    finally:
        await conn.disconnect()

asyncio.run(main())
```

**A note of honesty for the class:** the field names (`bms_state.soc`, `position`, `velocity`, `imu_state.rpy`) follow Unitree's standard sport-state schema, but haven't been independently confirmed against this specific robot. If the summary line comes back mostly empty, the script prints the raw payload's keys instead — treat that as the real answer, same lesson as the LIDAR section.

**Exercise for students:** graph battery percentage over a 5-minute walking session using `matplotlib`, sampling `stream_state` in a loop.

### Classroom activities (Stage 5/6 Computing)

- **`EC-DataSci`/`EC-DataViz`** Extend the battery-graphing exercise above into a small multi-panel dashboard that also plots velocity and roll/pitch/yaw over the same session, so battery drain can be visually correlated with how hard the robot was working.
- **`CT-Data`** Define what would count as an "outlier" reading in this stream (e.g. battery jumping from 80% to 20% in one sample) and write a simple sanity-check function that flags — but doesn't act on — suspicious readings.
- **`SE-Auto`** Write a first hand-rolled automation rule: read the battery level and refuse to run any further `walk_for()` calls below a threshold you choose, printing a warning instead. You'll meet a "real," more thorough version of this idea as `safety_watchdog.py` in Part 17 — compare your version to it once you get there.
- **`EC-Cyber`/`SE-Secure`** Telemetry here is read-only and gated only by the initial connection handshake, not by any further authentication. Discuss, in principle, what could go wrong if any device on the robot's network could silently read live position/orientation data — a genuine privacy/access-control question for a networked physical system.

---

## Part 6 — Odometry / path logging

Same module, different mode — logs the robot's reported pose over time to a CSV:

```bash
python -m go2_control.telemetry odometry --count 50 --out-csv odometry_log.csv
```

Pair this with Part 1's movement code: run a `walk_for()` sequence in one script while `log_odometry` runs in another, then plot the CSV afterward and compare the **actual** path to what the browser simulator predicted for the same routine. That comparison — intended motion vs. measured motion — is a genuinely open research-style question for students, since the simulator only ever shows intent.

### Classroom activities (Stage 5/6 Computing)

- **`SE-Proj`/`EC-Proj`** Turn the intended-vs-measured comparison above into a small scientific-method exercise: form a specific hypothesis first (e.g. "the robot turns wider than commanded on carpet than on tile"), design a measurement to test it, run it, and report your findings — including whether the data supported your hypothesis.
- **`EC-DataViz`** Record odometry under two different gait settings from Part 4 and overlay both paths as two lines on the same plot, so the effect of the gait choice on real-world drift is visible directly.
- **`CT-Mech`** Discuss why odometry (dead-reckoning from the robot's own reported pose) drifts over time, and how that differs in kind from LIDAR-based localisation (Part 3) — a genuine open problem in real mobile robotics, not something specific to this project.

---

## Part 7 — Audio playback

New module: [audio.py](go2_control/audio.py). Lists and plays the robot's built-in sounds through its onboard speaker.

```bash
python -m go2_control.audio list
python -m go2_control.audio play --id 1
```

Run `list` first — its response shows you the real ids/names available on this robot before you try to play anything. In Python:

```python
import asyncio
from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_control.audio import get_audio_list, play_audio

async def main():
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        print(await get_audio_list(conn))
        await play_audio(conn, "1")
    finally:
        await conn.disconnect()

asyncio.run(main())
```

**Exercise for students:** build a tiny "sound board" — a keyboard-driven script (reuse the `pynput` pattern from teleop) that plays a different sound on each key press.

### Classroom activities (Stage 5/6 Computing)

- **`CT-UX`/`EC-Media`** Extend the soundboard exercise above by designing (and justifying, in a sentence or two each) a mapping of specific sounds to specific robot states — e.g. a "low battery" sound, a "target lost" sound — that could later be wired into real automation in Part 9, 14, or 17.
- **`SE-Auto`** Connect Part 5's telemetry to Part 7's audio: trigger a sound automatically the moment a telemetry condition is met (e.g. low battery), rather than from a key press. This is a minimal but complete event-driven automation example — sense, decide, act.

---

## Part 8 — Reading the physical remote controller

New module: [remote_input.py](go2_control/remote_input.py). If you have the physical Unitree controller paired with the robot, this reads its live joystick/button state over WebRTC — purely observational, sends nothing.

```bash
python -m go2_control.remote_input --count 30
```

**Exercise for students:** have one student drive the robot with the physical remote while another runs this script and logs the raw values to a file — then write a small program that guesses which button/axis corresponds to "walk forward" purely from the logged data, without being told in advance.

### Classroom activities (Stage 5/6 Computing)

- **`CT-Net`** Diagram the three-way data flow between the physical remote, the robot, and your laptop running `remote_input.py`. Label which device is the "controller" and which is the "observer," and discuss whether more than one controller could conflict — a preview of Part 17's open question about simultaneous clients.
- **`EC-DataSci`** The button/axis-guessing exercise above is essentially hand-done supervised learning. Formalise your guess as an explicit rule (e.g. "if axis_2 > 0.5 then forward") and test whether it still holds against a second, independently logged recording.
- **`SE-Fund`** Write a handful of assertion-style checks against a saved log file (e.g. "when button X is pressed, field Y should be true within one message") — practice turning an observed pattern in real data into an explicit, testable specification.

---

## Part 9 — LED color, volume, brightness, and obstacle avoidance

New module: [experimental.py](go2_control/experimental.py). Unlike everything else in this section originally, these command IDs are **sourced from a real, working example script** in the actively-maintained `unitree_webrtc_connect` project (not guessed), so they're implemented for real:

```python
import asyncio
from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_control.experimental import set_led_color, set_volume, set_brightness, set_obstacle_avoidance

async def main():
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await set_led_color(conn, "purple", time_s=5.0)
        await set_volume(conn, 5)          # 0-10
        await set_brightness(conn, 8)      # 0-10
        await set_obstacle_avoidance(conn, True)
    finally:
        await conn.disconnect()

asyncio.run(main())
```

`set_led_color()` also supports a flashing color: pass `flash_cycle_ms=1000` for a color that blinks once per second. `get_volume()`, `get_brightness()`, and `get_obstacle_avoidance()` read the current setting back.

**Exercise for students:** write a "status light" function that changes LED color based on battery level from Part 5's telemetry — e.g. green above 50%, yellow above 20%, red below that.

**What's still not implemented, and why:** `start_slam_mapping()` (triggering onboard room-mapping mode) still raises `NotImplementedError` — no sourced command format was found for it, and guessing one risks sending an unverified command to a real robot. `watch_slam_topics()` remains fully safe and working (it only *listens*, never sends) — useful if SLAM is already running because someone started it from the Unitree phone app:

```python
from go2_control.experimental import watch_slam_topics
await watch_slam_topics(conn)   # inside the same connect()/disconnect() pattern as above
```

### Classroom activities (Stage 5/6 Computing)

- **`SE-Mech`/`CT-Mech`** Extend the status-light exercise above with hysteresis (e.g. don't switch from green to yellow until below 48%, and back to green only above 52%) so the light doesn't flicker right at the boundary — a real embedded-systems design problem, not just a bigger if/else chain.
- **`SE-Secure`/`EC-Cyber`** This module only implements command IDs "sourced from a real, working example," and explicitly refuses to guess `start_slam_mapping()`'s payload. Discuss why that discipline matters specifically because commands here reach real, physical hardware — connect it to responsible reverse-engineering practice and safety-critical systems design.
- **`SE-Auto`** Write a small automated "pre-flight check": before any script you write calls `walk_for()`, have it first confirm obstacle avoidance is enabled (using `get_obstacle_avoidance()`), enabling it automatically if it isn't.
- **`EC-Proj`** Write a one-page design document proposing a new "status" feature that combines LED, volume, and brightness for a specific real scenario (e.g. a warehouse robot signalling "busy," "idle," or "fault") — practice specifying a feature in writing before any code exists.

---

## Part 10 — Why "EDU-level" low-level joint control isn't on this list

A natural question once you've seen everything above: can this project reach the Go2 EDU tier's low-level motor control — direct per-joint position/velocity/torque commands that bypass the robot's own balance controller entirely?

**No, and this is worth teaching as its own lesson.** Two independent reasons:

1. **The library doesn't expose it.** The upstream WebRTC driver ships an example that *reads* low-level motor state (`rt/lf/lowstate` — joint angles, temperatures, battery), but there is no example anywhere in that project of *sending* a low-level motor command (`rt/lowcmd`). Only the high-level sport API, VUI, and obstacle-avoidance command paths are exposed for writing.
2. **The transport probably couldn't sustain it even if it were exposed.** Direct joint control needs a real-time loop running at roughly 500Hz–1kHz talking to the robot's internal DDS bus. Unitree's official low-level SDK (`unitree_sdk2`) reaches that bus over a wired Ethernet connection with native DDS — not over WebRTC, which was built for the phone app's control cadence, not a hard real-time control loop.

So this isn't a missing feature this project could add with more code — it would require different hardware wiring (Ethernet, not the WiFi hotspot everything else here uses) and an entirely different SDK. It's also meaningfully more dangerous: low-level commands bypass the balance controller, so a bad `kp`/`kd` gain can make the robot collapse or jerk unexpectedly — everything built in this project deliberately stays on the sport API precisely so that safety net stays in place.

**Discussion question for the class:** every capability in Parts 1–9 works because someone reverse-engineered the phone app's WebRTC traffic. Low-level control was deliberately *not* included in that reverse-engineered set. Why might Unitree's app — and by extension this whole ecosystem of community tools — never need to expose that path, even though the official EDU SDK has it?

### Classroom activities (Stage 5/6 Computing)

- **`SE-Secure`** Research why hard real-time control loops (500Hz–1kHz) can't tolerate the latency and jitter of a WebRTC-over-WiFi transport, and write a short explanation connecting real-time constraints to network architecture choices — a genuine systems-engineering topic, not just a Go2-specific fact.
- **`EC-Net`** Build a comparison table of wired Ethernet+DDS versus WebRTC-over-WiFi as two different networking architectures for control systems, covering latency, reliability, and security tradeoffs for each.
- **`CT-Mech`** Research what "low-level joint control" (position/velocity/torque, `kp`/`kd` gains) means physically in a legged robot, and explain in plain language what can go wrong if a bad gain value is sent — connecting mechatronics theory (PID/impedance control) to the software safety argument already made in the text above.

---

## Part 11 — Block-based programming

New tool: [block_ide.html](go2_control/block_ide.html) — a drag-and-drop, Scratch/Blockly-style editor covering everything in Parts 1–9 (movement, gait, gestures, camera, LIDAR, telemetry, LED/volume/brightness, obstacle avoidance, audio, wait, and repeat loops). It runs entirely in the browser — nothing it does talks to the robot directly.

### Launch it

```bash
cd go2_control
python3 -m http.server 8000
```

Open `http://localhost:8000/block_ide.html`.

### How it works

- Drag blocks from the categorized toolbox on the left into the workspace and snap them together, top to bottom.
- The right-hand panel shows the **real Python** your blocks produce, live, as you build — the exact same `client.method()` calls used everywhere else in this tutorial.
- Number fields on movement blocks are capped to the same limits enforced in `client.py` (walk speed ≤ 0.3 m/s, turn ≤ 1.0 rps) so an invalid value can't even be entered.
- Click **Save .py** to download the generated script, then run it exactly like any other script in this course:

    ```bash
    python go2_program.py
    ```

- There's no "Run" button that talks to the robot from the page. This is deliberate: every program still goes through the same review-then-run-from-a-terminal step as the rest of this tutorial, so nothing new bypasses the safety habits you've been building all along.

### Exercise for students

Recreate one of the CLI preset routines from Part 1 (e.g. `greet`: balance stand → wait → wave hello → wait → content → stop) purely by dragging blocks, save it, and run it. Then open the saved `.py` file in a text editor and compare it, line by line, to `run_routine()` in [cli.py](go2_control/cli.py) — same logic, two different ways of writing it.

**A caveat worth sharing with the class:** the block editor loads the Blockly library from a CDN (`unpkg.com`), so it needs internet access the first time the page loads in a session, even though the robot connection itself never does.

### Classroom activities (Stage 5/6 Computing)

- **`CT-Apps`/`CT-UX`** Extend the "recreate a preset routine" exercise above by identifying at least three concrete differences in how errors are prevented or possible in each representation (e.g. an invalid speed literally can't be entered in the block editor, but could be typed into raw Python before validation catches it at runtime).
- **`SE-Fund`** If you already know Python, "translate" one of your own scripts from Parts 1–9 into blocks by hand. Notice that the block IDE is really the same `Go2ControlClient` object/method model wearing a different interface — the underlying program is identical either way.
- **`EC-Cyber`** Discuss why the block editor needs internet access to load Blockly from a third-party CDN, and what a supply-chain risk of trusting that CDN would look like. Contrast this with why `go2_webrtc_connect` itself is vendored locally in this project rather than pulled live from PyPI on every install (see `CLAUDE.md`) — a real, contrasting design decision within the same codebase.

---

## Part 12 — Object detection and tracking (Machine Learning)

New module: [object_tracker.py](go2_control/object_tracker.py). This is **passive only** — it watches the camera feed and records where an object is over time. It never sends a movement command.

It uses a small pretrained YOLO model (via the `ultralytics` package) to recognize everyday objects — the same kind of model researchers and companies use for real object detection, not a toy example. It can recognize anything in the standard COCO class list: `person`, `sports ball`, `bottle`, `cell phone`, `dog`, `chair`, and 75 others.

### Install the extra dependencies (one-time)

```bash
pip install ultralytics opencv-python
```

The first run downloads the model weights (~6MB) from GitHub — if your school network blocks that, run it once somewhere with internet access first so the file is cached locally.

### Run it

```bash
python -m go2_control.object_tracker --target person --count 30 --interval 0.5
python -m go2_control.object_tracker --target "sports ball" --save-annotated
```

Each detection is logged to `object_track.csv` — timestamp, which frame, whether something was found, a persistent `track_id`, the class name, confidence, and its position as `(center_x, center_y)` normalized to `0.0–1.0` across the frame (`0.5, 0.5` is dead center). Rows where nothing was detected are logged too (`found=False`), so gaps in tracking show up clearly in the data. `--save-annotated` also saves a JPEG per frame with the bounding boxes drawn on it, so you can visually check the model got it right.

**Live preview, with IDs:** instead of logging to a file, you can watch detections happen in real time in a window on your own computer:

```bash
python -m go2_control.object_tracker --live --target person
python -m go2_control.object_tracker --live --all-classes   # show every class, not just one
```

This uses YOLO's built-in tracker (not just plain per-frame detection), so each object gets a `track_id` that stays the same across frames as long as it's trackable — if two people walk into frame, you'll see two different IDs, and each one keeps its own ID as they move, rather than the numbers resetting every frame. Press `q` to close the window. `--all-classes` also works with the CSV-logging mode above, if you want a full log of everything the camera sees rather than one specific class.

### How this connects to "training the robot with ML"

This tool answers the *detection* half of that question directly — `person`, `sports ball`, etc. are already trained into the model you're using. Two natural next projects build on top of it, in increasing order of difficulty:

1. **Recognize something the pretrained model doesn't know** (e.g. a specific toy, your school mascot) — capture images with your own camera and fine-tune a model on top of this same one. This is genuine ML training, using data your own camera collected. **Built in Part 15, below.**
2. **A "follow" behavior** — turn toward the object when it drifts off-center. This changes the safety picture (the robot now moves based on what a model thinks it sees, not just fixed pre-written commands), so it gets its own heavy guardrails. **Built in Part 14 (hand-coded) and Part 16 (learned from demonstration), below.**

**Exercise for students:** point the camera at a few different objects from the COCO list and compare confidence scores and how reliably each one gets detected — discuss why some objects (a person) are much more reliably detected than others (an unusual angle on a bottle), and what that implies about training data.

**Testing note:** verified end-to-end against the robot's real camera feed, including the live `--live`/`--all-classes` preview with persistent IDs — both the CSV-logging and live-window modes produced correct detections, positions, and stable per-object IDs during a real session. The tracker needs one extra package the first time you use `--live` or `--all-classes`: `pip install lap` (this is included automatically if you installed the `tracking` extra from `pyproject.toml`). If you're on the robot's WiFi (no internet) the first time you try it, that install will fail — run it once on your normal school/home WiFi first so it's cached locally.

### Classroom activities (Stage 5/6 Computing)

- **`EC-Intel`/`EC-DataSci`** Turn the confidence-comparison exercise above into a proper mini-experiment writeup: state a hypothesis, describe your method (which objects, how many trials each), present a results table, and write a conclusion — this practices the evaluation-of-AI-system-performance content central to the Intelligent systems module.
- **`SE-Auto`** The CSV logs `found=False` rows explicitly rather than skipping them. Explain, in writing, why that choice matters for any downstream automated decision-making that consumes this log (e.g. distinguishing "nothing there" from "the logger crashed").
- **`CT-Data`** Using just Python/`csv` (or `pandas` if available), compute summary statistics from `object_track.csv`: detection rate (% of rows with `found=True`), average confidence, and the longest gap between successful detections.
- **`EC-Cyber`** A camera on a network-connected robot streaming to any client that can reach it raises real privacy questions. Discuss what data-governance and consent considerations would apply if a robot like this were deployed somewhere public — a genuine Enterprise Computing ethics/legal topic, grounded in a system you've actually run.

---

## Part 13 — LIDAR-based object tracking

New module: [lidar_tracker.py](go2_control/lidar_tracker.py). Passive only — same as the camera version, it only watches and logs.

Since there's no pretrained "detector" for raw point clouds the way there is for camera images, this uses a simpler, fully explainable approach:

1. **Calibrate**: for the first `--calibrate-frames` messages, the space is assumed empty — every voxel (a coarse 3D grid cell) the LIDAR reports gets recorded as "background." **Clear the space before running this.**
2. **Track**: after that, any voxel that wasn't part of the background is "new" — grouped into clusters of touching voxels, and the centroid of the largest cluster is logged as the object's position.

```bash
python -m go2_control.lidar_tracker --calibrate-frames 10 --count 30 --out-csv lidar_track.csv
```

This is coarser than the camera version — it can't tell *what* the object is, only that something changed — and it will happily flag a chair being moved or a second person walking through as "the object." That's a feature for classroom discussion, not a bug to hide.

**Testing note:** the clustering/background-subtraction math (`_extract_points`, `_voxelize`, `_largest_cluster`) was unit-tested with synthetic point clouds during development and works correctly. What's still unverified — same caveat as Part 3 — is whether `_extract_points()` correctly parses the *real* decoded LIDAR payload shape, since that schema has never been confirmed against actual hardware. Run it once and check the console for "Could not find point data" warnings; if you see one, the payload's real keys are printed so you can fix the extraction logic.

**Exercise for students:** run both the camera tracker (Part 12) and this LIDAR tracker on the same moving object at the same time, then plot both trajectories together. Where do they agree? Where do they disagree, and why might that be (field of view, occlusion, voxel resolution)?

### Classroom activities (Stage 5/6 Computing)

- **`SE-Mech`** Before reading the implementation, describe `_voxelize` and `_largest_cluster` in plain English or as a flowchart, based only on the two-step explanation above. Then read the real code and compare — where did your description match, and where was the real algorithm more subtle?
- **`EC-Intel`** Compare this part's clustering approach (needs no training data, can't name what it found) against Part 12's camera tracker (needs a trained model, can name the class) as two different "intelligent systems" strategies. Write a short comparison of when you'd choose each in a real deployment.

---

## Part 14 — Actively following an object

New module: [follow.py](go2_control/follow.py). **This is the first script in this project where the robot moves based on what a live model thinks it sees, not a fixed pre-written sequence.** Read its printed safety banner before running it, and only use it in a clear, open space with someone ready to Ctrl+C or physically stop the robot.

```bash
python -m go2_control.follow --target person --max-seconds 20
```

It uses a simple proportional ("P") controller: the further off-center the object is, the harder the robot turns toward it; it only walks forward when the object is both roughly centered *and* not already close (using the bounding box's width as a rough distance proxy). Built-in safety layers, stacked:

- Every command still goes through `Go2ControlClient.move()`, so the 0.3 m/s / 1.0 rps caps from Part 1 still apply — a bad `--forward-speed` flag is rejected immediately at startup, not mid-run.
- Detections below `--min-confidence` (default 0.6) are ignored entirely, treated exactly the same as not seeing the object at all — the robot won't chase a low-confidence guess.
- If the object isn't seen for `--stale-timeout` seconds (default 1.0s), the robot **stops immediately**, every control tick, until it sees the object again.
- The whole run is capped at `--max-seconds` (default 30) regardless of what happens.
- Ctrl+C stops it instantly at any time.

**Exercise for students:** try `--max-turn-rps 0.15` vs the default `0.3` and discuss the tradeoff — a gentler turn is safer and smoother but may lose a fast-moving object; a sharper turn tracks better but overshoots more easily. This is the same tuning tradeoff every real visual-servoing system has to make.

### Classroom activities (Stage 5/6 Computing)

- **`SE-Auto`/`SE-Mech`** This is the clearest sense → decide → act automation loop in the whole tutorial. Draw it as a block diagram, and map each of the five safety layers listed above onto the diagram as an explicit checkpoint the loop passes through before a movement command is sent.
- **`SE-Secure`** Pick one safety layer (e.g. `--stale-timeout`) and write a short risk assessment for what would happen if it were removed: what fails, how likely is it in practice, and how bad is the outcome? This is genuine safety-critical-systems reasoning, applied to code you can actually read.
- **`CT-Mech`** Extend the turn-rate tuning exercise above into a systematic comparison: test at least three turn rates, three trials each, and pick a winner based on a metric you define in advance (e.g. time to re-center, or how often the object is lost).
- **`EC-Intel`** Discuss the ethical and safety implications of an autonomous robot deciding to move based on a machine-learning model's output rather than a direct human command. This is a real "intelligent systems" governance question, made concrete because your class actually built and ran the system being discussed.

---

## Part 15 — Training your own vision model

New modules: [dataset_capture.py](go2_control/dataset_capture.py), [train_classifier.py](go2_control/train_classifier.py), [recognize.py](go2_control/recognize.py). This is the full loop: capture your own images, train a real model on them, then run it live.

### 1. Capture images (once per class)

```bash
python -m go2_control.dataset_capture --label ball --count 40 --interval 0.3
python -m go2_control.dataset_capture --label shoe --count 40 --interval 0.3
```

Hold or point at each object while its capture runs — move it around a bit between shots so the model doesn't just memorize one exact pose. This saves into `dataset/train/<label>/` and `dataset/val/<label>/` automatically (the folder structure Ultralytics classification training expects).

### 2. Train

```bash
python -m go2_control.train_classifier --dataset-dir dataset --epochs 15
```

This fine-tunes a small pretrained classifier (`yolov8n-cls.pt`) on your images and prints a held-out accuracy so you can see how well it actually generalized, not just how well it memorized the training images. Saves to `trained_classifier.pt`.

### 3. Run it live

```bash
python -m go2_control.recognize --model trained_classifier.pt --count 20
```

### 4. Raising confidence

The pretrained model from Part 12 already knows 80 general-purpose COCO classes (`person`, `bottle`, `sports ball`, ...) reasonably well, because it was trained on hundreds of thousands of varied photos of each. Your model from step 2 is the opposite: it only knows what you showed it, so its confidence directly reflects how good and varied that data was. Concretely, low confidence usually comes from one (or more) of these:

- **Not enough images.** 10–20 images per class is barely enough to prove the pipeline works, not enough to generalize.
- **Not enough variety.** If every training image has the object in the same spot, same angle, same lighting, the model memorizes that one scene instead of learning what the object actually looks like. Move the object (or the robot) between shots.
- **A cluttered or inconsistent background.** If `ball` photos always have a red background and `shoe` photos never do, the model may partly be learning "background color," not "object shape" — it'll look confident in testing and then fail the moment the background changes.
- **Too few epochs**, or too many (the held-out accuracy printed in step 2 will actually go *down* if you overfit — watch for that, don't just assume more epochs is always better).

**Exercise for students — measure it, don't just guess:**

1. Pick an object that *isn't* one of the 80 pretrained COCO classes (so Part 12's generic detector can't recognize it at all — confidence 0, not even attempted).
2. Capture a small dataset (`--count 15`) and train (step 2). Run `recognize.py` and note the confidence.
3. Without changing anything else, capture a second, larger and more varied dataset for the *same* object (`--count 40`, different angles/lighting/positions this time) into a new folder, retrain, and run `recognize.py` again.
4. Compare the two confidence numbers directly. The gap *is* the effect of more/better data — that's the entire idea behind "training a model," made concrete instead of abstract.

**Testing note:** this entire pipeline — the exact dataset folder layout, the training call, and the resulting model's inference API — was run end-to-end during development against a real (synthetic) dataset and produced a working trained model file. This is the most thoroughly tested new capability in this project, short of actually pointing it at the robot's own camera.

**Exercise for students:** capture only 10 images per class instead of 40, retrain, and compare the held-out accuracy. Discuss why more (and more *varied*) data usually beats a bigger model for a small classification task like this.

### Classroom activities (Stage 5/6 Computing)

- **`EC-DataSci`/`EC-Intel`** Extend the measured confidence exercise above with a data-leakage thought experiment: what would happen to the reported held-out accuracy if the validation images were literally the same photos as the training images? Explain why that would be misleading, and check `dataset_capture.py` to confirm it actually keeps train/val images separate.
- **`SE-Auto`** Wire `dataset_capture.py`, `train_classifier.py`, and `recognize.py` into a single script (or Makefile) that runs the whole pipeline unattended from one command — practicing automation of a repeatable ML workflow, a genuine software-automation skill.
- **`SE-Proj`** Before capturing any images, write a short design note proposing a new object class relevant to your own school context (a specific tool, a mascot, a piece of sports equipment): how many images, what variety of angle/lighting/background, and why. Capture against your own plan and see how well it holds up.

---

## Part 16 — Training a "follow" behavior from your own demonstrations

New modules: [record_demo.py](go2_control/record_demo.py), [train_follow_policy.py](go2_control/train_follow_policy.py). Part 14's follow behavior was *hand-coded* — a human wrote the turn-toward-the-object formula. This part *learns* a follow behavior from labeled examples instead, and lets you compare the two directly.

### 1. Record demonstrations

```bash
python -m go2_control.record_demo --target person --count 60
```

For each detected frame, you're shown where the object is and asked to choose an action:

```
w = forward   a = turn left   d = turn right   s = stop/neutral   q = quit early
```

This never moves the robot — it's pure labeling. You're building a dataset of (what the camera saw → what a human would do), the same basic idea behind real imitation-learning/behavior-cloning systems.

### 2. Train a policy

```bash
python -m go2_control.train_follow_policy --data follow_demo.csv --out-policy follow_policy.json
```

This fits a small **linear regression** (via `numpy`, no ML framework needed) mapping the object's position/size to a `(forward, turn)` action. It's deliberately simple and transparent — `follow_policy.json` is a small, human-readable matrix of numbers, not a black box — and it reports mean absolute error on data it didn't train on, so you can see whether it actually generalized.

### 3. Run it — and compare

```bash
python -m go2_control.follow --target person --max-seconds 20 --policy follow_policy.json
```

All the same safety layers from Part 14 still apply — critically, **the trained policy's output is always clipped to the same speed caps as the hand-coded controller**, no matter what the model predicts. A model trained on 60 rows of your own labeling can't be trusted the same way as hand-verified code, so it never gets more authority than that.

**Exercise for students:** run the hand-coded controller (Part 14) and the trained policy (this part) back to back on the same object and compare how each one behaves. Then re-record demonstration data where you *deliberately* label inconsistently (sometimes turn left when the object's on the right, etc.) and retrain — watch the held-out error get worse, and discuss why: this is what "garbage in, garbage out" looks like with real numbers attached.

### Classroom activities (Stage 5/6 Computing)

- **`EC-Intel`** Name the ML paradigm used here explicitly (behaviour cloning / imitation learning) and build a short compare/contrast table across all three ML techniques you've now met: supervised classification (Part 15), unsupervised clustering (Part 13), and imitation learning (this part) — what data each needs, and what each is and isn't good for.
- **`SE-Secure`** The trained policy's output is always clipped to the same safety caps as the hand-coded controller — a textbook defence-in-depth pattern (never trust a model's output at full authority). Find at least one other place in this tutorial where the same "never trust it outright, clip or gate it" pattern appears (e.g. the speed caps in Part 1, or the `--min-confidence` gate in Part 14), and explain why it recurs.
- **`EC-DataSci`** Before training, plot or tabulate how consistent your own demonstration labels are for similar inputs (e.g. do you always label "object slightly right" as "turn right"?). Use this as a data-quality check to predict, before training, whether your policy will generalize well.

---

## Part 17 — Independent capture and monitoring devices

New modules: [capture_logger.py](go2_control/capture_logger.py), [passive_recorder.py](go2_control/passive_recorder.py), [inference_appliance.py](go2_control/inference_appliance.py), [safety_watchdog.py](go2_control/safety_watchdog.py). These don't add a new robot capability — they reuse the same camera/LIDAR/telemetry/audio access every other script in this tutorial uses. What's different is *where* they run: each is built to run unattended, on a second device, decoupled from whatever else is controlling the robot. Any device that joins the robot's own WiFi hotspot and speaks WebRTC is a legitimate client, the same way the official app is — nothing here needs special permission from Unitree.

### Untethered capture rig

`capture_logger.py` logs camera + LIDAR + telemetry together into one timestamped session folder. Built to run on a battery-powered Raspberry Pi or Jetson riding the Picatinny mount kit rather than a laptop on a leash — it takes a `--duration` in seconds rather than a frame count, and prints one heartbeat line every 10 seconds instead of a line per frame, so it stays readable if you're tailing a log file over SSH.

```bash
python -m go2_control.capture_logger --duration 300
```

```bash
python -m go2_control.capture_logger --duration 600 --out-dir capture_sessions --camera-interval 2.0
```

### Passive recorder for remote-driven sessions

`passive_recorder.py` never sends a movement command. Run it on a laptop while a second person drives the robot with its *physical* remote — which drives reliably, unlike this project's own `Move` command (Part 1) — and it pairs each saved camera frame with the robot's own telemetry (battery, velocity, roll/pitch/yaw) at that exact moment into one CSV. That gives you a ready-to-train (image → robot state) dataset directly, instead of three separate logs you'd have to align by timestamp afterward.

```bash
python -m go2_control.passive_recorder --duration 600
```

### Headless inference appliance

`inference_appliance.py` is Part 12's `object_tracker.py --live` with the on-screen window removed — for a headless device with no display attached, watching continuously as a standing perception station independent of whoever is driving. It needs the same `ultralytics` package as Part 12; `opencv-python` is only required if you use `--save-snapshots`.

```bash
python -m go2_control.inference_appliance --duration 1800
```

```bash
python -m go2_control.inference_appliance --target person --save-snapshots --snapshot-every 60
```

`--save-snapshots` saves one annotated JPEG every `--snapshot-every` seconds (not every frame), so you can spot-check accuracy later without ever needing a live display.

### Independent safety watchdog

`safety_watchdog.py` is read-only — it watches battery level and tilt (roll/pitch) and never sends a command, so it can run on its own device alongside anything else and keeps watching even if your main control script crashes.

```bash
python -m go2_control.safety_watchdog
```

```bash
python -m go2_control.safety_watchdog --min-battery 20 --max-tilt-deg 35 --audio-alert
```

It only alerts once per threshold breach, then re-arms once the value recovers, so it won't spam the same warning every message. `--audio-alert` also plays a sound through the robot's own speaker (Part 7) the moment it fires.

**Testing note:** these four scripts were checked statically this session — they compile, every import resolves against the real driver, and a full cross-module audit confirmed no leftover references to renamed functions — but none has been run against the robot yet. Same rule as everywhere else in this project: treat them as unverified until someone actually runs them on hardware.

**Exercise for students:** run `capture_logger.py` on one laptop and `safety_watchdog.py --audio-alert` on a second, at the same time. Every script in this project opens its own connection and disconnects independently (see `CLAUDE.md`), so this is also the fastest way to find out firsthand whether the robot's WebRTC signaling actually supports more than one simultaneous client — an open question nothing in this project has answered yet.

### Classroom activities (Stage 5/6 Computing)

- **`CT-Net`/`EC-Net`** Before running the simultaneous-clients exercise above, research or predict whether WebRTC signaling typically supports more than one client at once, and write down your prediction. Run the exercise, then compare your prediction to what actually happened.
- **`SE-Auto`/`SE-Proj`** Design (a short written spec, not full code) a fifth independent device not yet built — e.g. an automatic low-battery "return toward dock" trigger. Describe what it senses, what it decides, what it does, and specifically why it should run on its own device rather than inside the main control script (separation of concerns / fault isolation — a real software-automation architecture principle).
- **`EC-Cyber`** All four of these devices connect to the robot's open hotspot with no authentication beyond WebRTC's own handshake. Research what a minimal access-control layer would look like if a system like this were deployed somewhere less controlled than a classroom, and write a short recommendation.

---

## Capstone project ideas (Stage 5/6 assessment)

Everything above is a guided exercise; the ideas below are open enough to anchor a full assessment task, sized for the project component every one of these courses ends on (a Stage 5 combined-focus-area project, `SE-Proj`, or `EC-Proj`).

1. **Automated patrol with reporting** (`SE-Proj` / `EC-Proj` / `CT-Mech` + `CT-Data`). Combine Part 1 (movement), Part 5 (telemetry), Part 12 (object detection), and Part 17 (independent logging) into a script that walks a short fixed route, logs everything it sees, and produces a short automatically-generated summary report at the end (objects seen, battery used, any safety thresholds crossed). Marking criteria split naturally along: correctness of the control logic, quality/format of the logged data, and how well the report communicates results to a non-technical reader.
2. **Learned vs. hand-coded behaviour comparison study** (`SE-Mech` / `EC-Intel`). Use Parts 14 and 16 to build both a hand-coded and a trained "follow" controller for the same task, then design and run a fair, repeatable comparison (same object, same lighting, same number of trials) and write it up as a short empirical report — close to genuine ML-systems evaluation methodology.
3. **Safety-case documentation exercise** (`SE-Secure` / `EC-Cyber`). Working entirely from the existing codebase (no new code required), produce a short "safety case" document: list every safety layer you can find across Parts 1, 9, 14, and 17 (speed caps, blocked acrobatic commands, stale-timeout stop, confidence gate, watchdog thresholds), explain what failure each one prevents, and identify one gap the current project doesn't cover. This doubles as a close-reading exercise in a real, non-trivial codebase.
4. **Custom object recognition mini-enterprise** (`EC-DataSci` / `EC-Proj`). Pick a genuine "enterprise" framing — e.g. a lost-property recognition tool for the school — and take it through the full Part 15 pipeline (capture → train → evaluate → recognise live), with a written justification of dataset design decisions and a discussion of where the system would fail in production and why.
5. **New independent device** (`SE-Auto` / `CT-Mech`). Design and build a genuinely new module for Part 17 (e.g. an automatic LED status beacon that reflects battery and tilt from Part 5's telemetry, running as its own decoupled process) — the smallest new piece of automation a student can add without touching movement code at all, making it a safe first "own idea" project.

---

## Quick reference — all commands in one place

```bash
# Setup
source .venv/bin/activate
ping 192.168.12.1

# Movement
python -m go2_control.cli stand-up
python -m go2_control.cli menu
python -m go2_control.cli routine greet

# Before handing the robot to a student for the app or physical remote
python -m go2_control.cli routine handoff

# Camera
python -m go2_control.camera_view --count 10
python -m go2_control.camera_view --live

# LIDAR
python -m go2_control.lidar_view --count 20
python -m go2_control.lidar_view --record --out-dir lidar_recording

# Telemetry / odometry (read-only, safe any time)
python -m go2_control.telemetry state --count 20
python -m go2_control.telemetry odometry --count 50 --out-csv odometry_log.csv

# Audio
python -m go2_control.audio list
python -m go2_control.audio play --id 1

# Physical remote (read-only)
python -m go2_control.remote_input --count 30

# LED / volume / brightness / obstacle avoidance (run from your own script, see Part 9)

# Object detection & tracking (pip install ultralytics opencv-python)
python -m go2_control.object_tracker --target person --count 30
python -m go2_control.lidar_tracker --calibrate-frames 10 --count 30

# Active following (moves the robot -- read the safety banner first)
python -m go2_control.follow --target person --max-seconds 20

# Train your own vision model
python -m go2_control.dataset_capture --label ball --count 40
python -m go2_control.train_classifier --dataset-dir dataset --epochs 15
python -m go2_control.recognize --model trained_classifier.pt --count 20

# Train a follow behavior from demonstration
python -m go2_control.record_demo --target person --count 60
python -m go2_control.train_follow_policy --data follow_demo.csv --out-policy follow_policy.json
python -m go2_control.follow --target person --policy follow_policy.json

# Independent capture / monitoring devices (own device, decoupled from the main control script)
python -m go2_control.capture_logger --duration 300
python -m go2_control.passive_recorder --duration 600
python -m go2_control.inference_appliance --duration 1800
python -m go2_control.safety_watchdog --min-battery 20 --max-tilt-deg 35 --audio-alert
```

## Troubleshooting

| Problem | Fix |
|---|---|
| ping gets no reply | Re-check WiFi is joined to UNITREE_GO2, and the robot has finished booting |
| Script hangs at "Data channel did not open in time" | Robot is off, out of range, or already controlled by the mobile app — close the app and retry |
| --live camera preview fails to import cv2 | pip install opencv-python |
| Relative import error running a file directly | Use the module form, e.g. python -m go2_control.camera_view, not python go2_control/camera_view.py |
| telemetry/audio field names don't match what's in this tutorial | Print the raw payload — schemas here are traced from library source, not hardware-verified; treat the real output as ground truth |
| start_slam_mapping() raises NotImplementedError | Expected — see Part 9, no sourced command format exists for it yet |
| Wondering why there's no low-level joint control | Expected — see Part 10, it isn't reachable through this project's transport at all |
| ultralytics/YOLO scripts fail with "No module named 'ultralytics'" | pip install ultralytics opencv-python (Parts 12–16) |
| First ML run is slow or needs internet | It's downloading model weights (~6MB) the first time — run once with internet access so it's cached locally afterward |
| A console warning about duplicate AVFFrameReceiver/libavdevice classes | Harmless in testing so far, but comes from opencv-python and av both bundling their own ffmpeg libraries in the same process (Parts 12–16 use both). If you see actual crashes rather than just the warning, report it — it may need one of the two packages pinned to a version without the conflict |
| follow.py or record_demo.py don't seem to react to the object | Check --target matches a real COCO class name exactly (e.g. "sports ball", not "ball") — run object_tracker.py first to confirm detection is working before layering movement or recording on top |
