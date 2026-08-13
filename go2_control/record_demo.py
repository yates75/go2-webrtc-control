"""Record training data for a learned "follow" behavior by demonstration.

For each detected frame of --target, you (the human) choose what the
robot should do by pressing a key -- forward, turn left, turn right, or
stop. Each choice is logged alongside where the object actually was in
frame, building a (what the camera saw -> what a human would do) dataset.
train_follow_policy.py then fits a small model to that dataset, and
follow.py can drive using the learned model instead of (or compared
against) its hand-coded proportional controller.

This script never moves the robot itself -- it's pure labeling. Point
the camera (e.g. hold the robot, or have it already standing) at the
target object moving around, and label what you'd do to follow it.

Usage:
    python -m go2_control.record_demo --target person --count 60
Keys while running:
    w = forward   a = turn left   d = turn right   s = stop/neutral   q = quit early
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import termios
import time
import tty
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from go2_webrtc_driver.go2_webrtc_connection import (
        Go2WebRTCConnection,
        WebRTCConnectionMethod,
    )
except ModuleNotFoundError:
    from go2_webrtc_driver.webrtc_driver import (
        Go2WebRTCConnection,
        WebRTCConnectionMethod,
    )

from go2_control.camera_view import stream_camera
from go2_control.object_tracker import _load_model, _tracked_detections

FORWARD_STEP = 0.1
TURN_STEP = 0.3

KEY_ACTIONS = {
    "w": ("forward", FORWARD_STEP, 0.0),
    "a": ("turn left", 0.0, TURN_STEP),
    "d": ("turn right", 0.0, -TURN_STEP),
    "s": ("stop", 0.0, 0.0),
}


def _get_key() -> str:
    """Blocking single-keypress read from the terminal (POSIX only)."""

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


async def record(
    conn: Go2WebRTCConnection,
    target_class: str,
    count: int,
    detect_interval: float,
    out_csv: Path,
) -> None:
    model = _load_model()
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    logged = 0
    quit_requested = False
    last_detect = 0.0
    lock = asyncio.Lock()
    done = asyncio.Event()

    print("Recording demonstration data.")
    print("Keys: w=forward  a=turn left  d=turn right  s=stop/neutral  q=quit early\n")

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["center_x", "center_y", "box_w", "box_h", "forward_mps", "turn_rps"])

        async def on_frame(frame) -> None:
            nonlocal logged, last_detect, quit_requested
            if quit_requested or logged >= count:
                return

            now = time.monotonic()
            if now - last_detect < detect_interval:
                return
            last_detect = now

            img = frame.to_ndarray(format="bgr24")
            _, matches = await asyncio.to_thread(_tracked_detections, model, img, target_class)
            best = max(matches, key=lambda m: m["confidence"]) if matches else None
            if best is None:
                return

            if lock.locked():
                return  # still waiting on a previous keypress; skip this frame

            async with lock:
                print(
                    f"[{logged}/{count}] {target_class} at "
                    f"x={best['center_x']:.2f} y={best['center_y']:.2f} size={best['box_w']:.2f} -- action? ",
                    end="",
                    flush=True,
                )
                key = await asyncio.to_thread(_get_key)
                print(key)

                if key == "q":
                    quit_requested = True
                    done.set()
                    return
                if key not in KEY_ACTIONS:
                    print("  (unrecognized key, skipped)")
                    return

                label, forward, turn = KEY_ACTIONS[key]
                writer.writerow([best["center_x"], best["center_y"], best["box_w"], best["box_h"], forward, turn])
                handle.flush()
                print(f"  logged: {label} (forward={forward}, turn={turn})")

                logged += 1
                if logged >= count:
                    done.set()

        await stream_camera(conn, on_frame)
        await done.wait()

    print(f"\nRecorded {logged} demonstration rows to {out_csv}")


async def main_async(target: str, count: int, detect_interval: float, out_csv: Path) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await record(conn, target, count, detect_interval, out_csv)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Record (object position -> human action) demonstration data")
    parser.add_argument("--target", default="person", help="COCO class name to demonstrate following")
    parser.add_argument("--count", type=int, default=60, help="Number of labeled samples to collect")
    parser.add_argument("--detect-interval", type=float, default=0.5, help="Minimum seconds between prompts")
    parser.add_argument("--out-csv", default="follow_demo.csv", help="CSV output path")
    args = parser.parse_args()

    try:
        asyncio.run(main_async(args.target, args.count, args.detect_interval, Path(args.out_csv)))
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
