"""Passive recorder pairing camera frames with robot state -- for building supervised training data.

Meant to run on its own device while a human drives the robot with its
physical remote (which drives reliably, unlike this project's `Move`
command) -- this script never sends a movement command, it only watches.
Each saved image gets a row of the robot's own telemetry (battery,
velocity, roll/pitch/yaw) closest in time to when it was captured, so the
output is directly usable as (image -> robot state) training pairs rather
than separate logs that need aligning afterwards.

Usage:
    python -m go2_control.passive_recorder --duration 600
    python -m go2_control.passive_recorder --duration 1200 --interval 0.5 --out-dir demo_sessions
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import time
from datetime import datetime
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
from go2_webrtc_driver.constants import RTC_TOPIC

from go2_control.camera_view import stream_camera
from go2_control.telemetry import _unwrap


def _state_fields(payload: dict) -> dict:
    """Pull out the numeric fields worth pairing with an image, defensively.

    Field names follow the standard Unitree sport-state schema but, like
    telemetry.py, haven't been independently confirmed against this robot's
    firmware -- missing fields are left blank rather than raising.
    """

    bms = payload.get("bms_state")
    battery = bms.get("soc") if isinstance(bms, dict) else None

    velocity = payload.get("velocity")
    vx, vy, vyaw = (velocity + [None, None, None])[:3] if isinstance(velocity, list) else (None, None, None)

    imu_state = payload.get("imu_state")
    rpy = imu_state.get("rpy") if isinstance(imu_state, dict) else None
    roll, pitch, yaw = (rpy + [None, None, None])[:3] if isinstance(rpy, list) else (None, None, None)

    return {"battery": battery, "vel_x": vx, "vel_y": vy, "vel_yaw": vyaw, "roll": roll, "pitch": pitch, "yaw": yaw}


async def record(conn: Go2WebRTCConnection, session_dir: Path, duration_s: float, interval_s: float) -> None:
    image_dir = session_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    out_csv = session_dir / "pairs.csv"

    await conn.datachannel.disableTrafficSaving(True)

    latest_state: dict = {}
    state_topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]

    def on_state(message: dict) -> None:
        latest_state.update(_state_fields(_unwrap(message)))

    for topic in state_topics:
        conn.datachannel.pub_sub.subscribe(topic, on_state)

    saved = 0
    last_saved = 0.0
    stop = asyncio.Event()

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["image", "timestamp", "battery", "vel_x", "vel_y", "vel_yaw", "roll", "pitch", "yaw"])

        async def on_frame(frame) -> None:
            nonlocal saved, last_saved
            now = time.monotonic()
            if now - last_saved < interval_s:
                return
            last_saved = now

            image_path = image_dir / f"frame_{saved:05d}.jpg"
            frame.to_image().save(image_path)
            state = latest_state.copy()
            writer.writerow(
                [
                    image_path.name,
                    time.time(),
                    state.get("battery"),
                    state.get("vel_x"),
                    state.get("vel_y"),
                    state.get("vel_yaw"),
                    state.get("roll"),
                    state.get("pitch"),
                    state.get("yaw"),
                ]
            )
            handle.flush()
            saved += 1
            if saved % 20 == 0:
                print(f"[{saved}] {image_path.name} state={state}")

        await stream_camera(conn, on_frame)
        print(f"Recording to {session_dir} for {duration_s:.0f}s (Ctrl-C to stop early)...")
        try:
            await asyncio.wait_for(stop.wait(), timeout=duration_s)
        except asyncio.TimeoutError:
            pass
        finally:
            for topic in state_topics:
                conn.datachannel.pub_sub.unsubscribe(topic)

    print(f"Recorded {saved} image/state pairs -> {out_csv}")


async def main_async(out_dir: Path, duration: float, interval: float) -> None:
    session_dir = out_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await record(conn, session_dir, duration, interval)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Passively record (camera frame -> robot state) pairs while a human drives with the physical remote"
    )
    parser.add_argument("--duration", type=float, default=600.0, help="Seconds to record before stopping")
    parser.add_argument("--interval", type=float, default=0.5, help="Seconds between saved image/state pairs")
    parser.add_argument("--out-dir", default="demo_sessions", help="Parent directory for timestamped session folders")
    args = parser.parse_args()

    try:
        asyncio.run(main_async(Path(args.out_dir), args.duration, args.interval))
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
