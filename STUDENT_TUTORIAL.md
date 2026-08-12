# Go2 WebRTC Control — Student Tutorial

A hands-on tutorial for driving the Unitree Go2 Pro, viewing its camera feed, and viewing/recording its LIDAR feed with Python.

**Read this first:** this robot is a real physical machine. Always work in a clear, open space, keep hands and feet away from the legs while it moves, and never run a command you don't understand yet. Every movement command in this project is speed-limited to keep things safe — don't remove those limits.

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

Full list: `greet`, `calm-start`, `short-walk`, `reset`, `turn-left`, `turn-right`, `back-up-slowly`.

**Exercise for students:** open [cli.py](go2_control/cli.py) and find `run_routine()`. Add a new routine name (e.g. `"figure-eight"`) that chains a left turn and a right turn together, using only the safe methods above.

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

---

## Part 6 — Odometry / path logging

Same module, different mode — logs the robot's reported pose over time to a CSV:

```bash
python -m go2_control.telemetry odometry --count 50 --out-csv odometry_log.csv
```

Pair this with Part 1's movement code: run a `walk_for()` sequence in one script while `log_odometry` runs in another, then plot the CSV afterward and compare the **actual** path to what the browser simulator predicted for the same routine. That comparison — intended motion vs. measured motion — is a genuinely open research-style question for students, since the simulator only ever shows intent.

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

---

## Part 8 — Reading the physical remote controller

New module: [remote_input.py](go2_control/remote_input.py). If you have the physical Unitree controller paired with the robot, this reads its live joystick/button state over WebRTC — purely observational, sends nothing.

```bash
python -m go2_control.remote_input --count 30
```

**Exercise for students:** have one student drive the robot with the physical remote while another runs this script and logs the raw values to a file — then write a small program that guesses which button/axis corresponds to "walk forward" purely from the logged data, without being told in advance.

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

---

## Part 10 — Why "EDU-level" low-level joint control isn't on this list

A natural question once you've seen everything above: can this project reach the Go2 EDU tier's low-level motor control — direct per-joint position/velocity/torque commands that bypass the robot's own balance controller entirely?

**No, and this is worth teaching as its own lesson.** Two independent reasons:

1. **The library doesn't expose it.** The upstream WebRTC driver ships an example that *reads* low-level motor state (`rt/lf/lowstate` — joint angles, temperatures, battery), but there is no example anywhere in that project of *sending* a low-level motor command (`rt/lowcmd`). Only the high-level sport API, VUI, and obstacle-avoidance command paths are exposed for writing.
2. **The transport probably couldn't sustain it even if it were exposed.** Direct joint control needs a real-time loop running at roughly 500Hz–1kHz talking to the robot's internal DDS bus. Unitree's official low-level SDK (`unitree_sdk2`) reaches that bus over a wired Ethernet connection with native DDS — not over WebRTC, which was built for the phone app's control cadence, not a hard real-time control loop.

So this isn't a missing feature this project could add with more code — it would require different hardware wiring (Ethernet, not the WiFi hotspot everything else here uses) and an entirely different SDK. It's also meaningfully more dangerous: low-level commands bypass the balance controller, so a bad `kp`/`kd` gain can make the robot collapse or jerk unexpectedly — everything built in this project deliberately stays on the sport API precisely so that safety net stays in place.

**Discussion question for the class:** every capability in Parts 1–9 works because someone reverse-engineered the phone app's WebRTC traffic. Low-level control was deliberately *not* included in that reverse-engineered set. Why might Unitree's app — and by extension this whole ecosystem of community tools — never need to expose that path, even though the official EDU SDK has it?

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

---

## Part 14 — Actively following an object

New module: [follow.py](go2_control/follow.py). **This is the first script in this project where the robot moves based on what a live model thinks it sees, not a fixed pre-written sequence.** Read its printed safety banner before running it, and only use it in a clear, open space with someone ready to Ctrl+C or physically stop the robot.

```bash
python -m go2_control.follow --target person --max-seconds 20
```

It uses a simple proportional ("P") controller: the further off-center the object is, the harder the robot turns toward it; it only walks forward when the object is both roughly centered *and* not already close (using the bounding box's width as a rough distance proxy). Built-in safety layers, stacked:

- Every command still goes through `Go2ControlClient.move()`, so the 0.3 m/s / 1.0 rps caps from Part 1 still apply — a bad `--forward-speed` flag is rejected immediately at startup, not mid-run.
- If the object isn't seen for `--stale-timeout` seconds (default 1.0s), the robot **stops immediately**, every control tick, until it sees the object again.
- The whole run is capped at `--max-seconds` (default 30) regardless of what happens.
- Ctrl+C stops it instantly at any time.

**Exercise for students:** try `--max-turn-rps 0.15` vs the default `0.3` and discuss the tradeoff — a gentler turn is safer and smoother but may lose a fast-moving object; a sharper turn tracks better but overshoots more easily. This is the same tuning tradeoff every real visual-servoing system has to make.

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