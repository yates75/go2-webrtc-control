"""Untethered capture rig: log camera, LIDAR, and telemetry together to one session folder.

Meant to run on a battery-powered SBC (Raspberry Pi, Jetson) riding the
Picatinny mount kit rather than a tethered laptop -- one connection, one
command, self-contained output, safe to leave running unattended (e.g.
under `nohup` or a systemd unit) for the whole session. Prints a periodic
heartbeat instead of per-frame spam so it stays readable in a log file.

Usage:
    python -m go2_control.capture_logger --duration 300
    python -m go2_control.capture_logger --duration 600 --out-dir capture_sessions --camera-interval 2.0
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import pickle
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
from go2_control.telemetry import _summarize_state, _unwrap


async def _log_camera(conn: Go2WebRTCConnection, out_dir: Path, interval_s: float, stop: asyncio.Event, counters: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    last_saved = 0.0

    async def on_frame(frame) -> None:
        nonlocal last_saved
        if stop.is_set():
            return
        now = time.monotonic()
        if now - last_saved < interval_s:
            return
        last_saved = now
        image_path = out_dir / f"frame_{counters['camera']:05d}.jpg"
        frame.to_image().save(image_path)
        counters["camera"] += 1

    await stream_camera(conn, on_frame)


async def _log_lidar(conn: Go2WebRTCConnection, out_dir: Path, interval_s: float, stop: asyncio.Event, counters: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    last_saved = 0.0

    def on_message(message: dict) -> None:
        nonlocal last_saved
        if stop.is_set():
            return
        now = time.monotonic()
        if now - last_saved < interval_s:
            return
        last_saved = now
        payload = message["data"]["data"]
        frame_path = out_dir / f"frame_{counters['lidar']:04d}.pkl"
        with frame_path.open("wb") as handle:
            pickle.dump(payload, handle)
        counters["lidar"] += 1

    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["ULIDAR_ARRAY"], on_message)
    conn.datachannel.pub_sub.publish_without_callback(RTC_TOPIC["ULIDAR_SWITCH"], "on")
    try:
        await stop.wait()
    finally:
        conn.datachannel.pub_sub.unsubscribe(RTC_TOPIC["ULIDAR_ARRAY"])
        conn.datachannel.pub_sub.publish_without_callback(RTC_TOPIC["ULIDAR_SWITCH"], "off")


async def _log_telemetry(conn: Go2WebRTCConnection, out_csv: Path, stop: asyncio.Event, counters: dict) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    state_topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "summary"])

        def on_message(message: dict) -> None:
            if stop.is_set():
                return
            writer.writerow([time.time(), _summarize_state(_unwrap(message))])
            handle.flush()
            counters["telemetry"] += 1

        for topic in state_topics:
            conn.datachannel.pub_sub.subscribe(topic, on_message)
        try:
            await stop.wait()
        finally:
            for topic in state_topics:
                conn.datachannel.pub_sub.unsubscribe(topic)


async def _heartbeat(stop: asyncio.Event, counters: dict, every_s: float = 10.0) -> None:
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=every_s)
        except asyncio.TimeoutError:
            print(f"[heartbeat] camera={counters['camera']} lidar={counters['lidar']} telemetry={counters['telemetry']}")


async def run_session(
    conn: Go2WebRTCConnection,
    session_dir: Path,
    duration_s: float,
    camera_interval_s: float,
    lidar_interval_s: float,
) -> None:
    await conn.datachannel.disableTrafficSaving(True)

    counters = {"camera": 0, "lidar": 0, "telemetry": 0}
    stop = asyncio.Event()

    tasks = [
        asyncio.create_task(_log_camera(conn, session_dir / "camera", camera_interval_s, stop, counters)),
        asyncio.create_task(_log_lidar(conn, session_dir / "lidar", lidar_interval_s, stop, counters)),
        asyncio.create_task(_log_telemetry(conn, session_dir / "telemetry.csv", stop, counters)),
        asyncio.create_task(_heartbeat(stop, counters)),
    ]

    print(f"Recording to {session_dir} for {duration_s:.0f}s (Ctrl-C to stop early)...")
    try:
        await asyncio.wait_for(stop.wait(), timeout=duration_s)
    except asyncio.TimeoutError:
        pass
    finally:
        stop.set()
        await asyncio.gather(*tasks, return_exceptions=True)

    print(
        f"Session complete: {counters['camera']} camera frames, {counters['lidar']} lidar frames, "
        f"{counters['telemetry']} telemetry rows -> {session_dir}"
    )


async def main_async(out_dir: Path, duration: float, camera_interval: float, lidar_interval: float) -> None:
    session_dir = out_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await run_session(conn, session_dir, duration, camera_interval, lidar_interval)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Log camera, LIDAR, and telemetry together to one session folder (untethered capture rig)"
    )
    parser.add_argument("--duration", type=float, default=300.0, help="Seconds to record before stopping")
    parser.add_argument("--out-dir", default="capture_sessions", help="Parent directory for timestamped session folders")
    parser.add_argument("--camera-interval", type=float, default=1.0, help="Seconds between saved camera frames")
    parser.add_argument("--lidar-interval", type=float, default=1.0, help="Seconds between saved lidar frames")
    args = parser.parse_args()

    try:
        asyncio.run(main_async(Path(args.out_dir), args.duration, args.camera_interval, args.lidar_interval))
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
