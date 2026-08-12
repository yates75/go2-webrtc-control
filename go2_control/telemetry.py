"""Read-only robot telemetry: battery, IMU orientation, velocity, and odometry.

Subscribes to the Go2's own state topics -- no commands are sent, so this
is safe to run at any time, including while the robot is standing still
or being driven by something else.

Field names below follow the standard Unitree Go2 sport-state schema but
haven't been independently confirmed against this specific robot's
firmware. If the summarized fields come back empty, the script falls back
to printing the raw payload's keys so you can see the real field names.

Usage:
    python -m go2_control.telemetry state --count 20
    python -m go2_control.telemetry odometry --count 50 --out-csv odometry_log.csv
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import time
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


def _unwrap(message: dict) -> dict:
    """Pull the actual state payload out of the pub/sub message envelope."""

    data = message.get("data", {})
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        return data["data"]
    return data if isinstance(data, dict) else {}


def _summarize_state(payload: dict) -> str:
    """Best-effort summary of common Unitree sport-state fields."""

    battery = payload.get("bms_state", {}).get("soc") if isinstance(payload.get("bms_state"), dict) else None
    position = payload.get("position")
    velocity = payload.get("velocity")
    imu_state = payload.get("imu_state")
    rpy = imu_state.get("rpy") if isinstance(imu_state, dict) else None

    parts = []
    if battery is not None:
        parts.append(f"battery={battery}%")
    if position is not None:
        parts.append(f"position={position}")
    if velocity is not None:
        parts.append(f"velocity={velocity}")
    if rpy is not None:
        parts.append(f"roll_pitch_yaw={rpy}")
    return ", ".join(parts) if parts else f"raw keys: {list(payload.keys())}"


async def stream_state(conn: Go2WebRTCConnection, count: int) -> None:
    """Print `count` summarized sport-state messages, then stop."""

    received = 0
    done = asyncio.Event()

    def on_message(message: dict) -> None:
        nonlocal received
        print(f"[{received}] {_summarize_state(_unwrap(message))}")
        received += 1
        if received >= count:
            done.set()

    # Firmware varies on whether sport state is published under the classic
    # topic or the newer "lf" (low-frequency) one -- subscribe to both and
    # take whichever the robot actually sends.
    state_topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]
    for topic in state_topics:
        conn.datachannel.pub_sub.subscribe(topic, on_message)
    try:
        await asyncio.wait_for(done.wait(), timeout=30.0)
    except asyncio.TimeoutError:
        print(f"Only received {received}/{count} state messages in 30s -- stopping.")
    finally:
        for topic in state_topics:
            conn.datachannel.pub_sub.unsubscribe(topic)


async def log_odometry(conn: Go2WebRTCConnection, count: int, out_csv: Path) -> None:
    """Log `count` raw pose messages (timestamp + payload) to a CSV file."""

    received = 0
    done = asyncio.Event()
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "raw_pose"])

        def on_message(message: dict) -> None:
            nonlocal received
            writer.writerow([time.time(), _unwrap(message)])
            handle.flush()
            received += 1
            if received >= count:
                done.set()

        conn.datachannel.pub_sub.subscribe(RTC_TOPIC["ROBOTODOM"], on_message)
        try:
            await asyncio.wait_for(done.wait(), timeout=30.0)
        except asyncio.TimeoutError:
            print(f"Only received {received}/{count} odometry messages in 30s -- stopping.")
        finally:
            conn.datachannel.pub_sub.unsubscribe(RTC_TOPIC["ROBOTODOM"])

    print(f"Logged {received} odometry rows to {out_csv}")


async def main_async(mode: str, count: int, out_csv: Path | None) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    await conn.datachannel.disableTrafficSaving(True)
    try:
        if mode == "state":
            await stream_state(conn, count)
        else:
            await log_odometry(conn, count, out_csv or Path("odometry_log.csv"))
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only telemetry from the Go2 (no commands sent)")
    parser.add_argument("mode", choices=["state", "odometry"], help="What to stream")
    parser.add_argument("--count", type=int, default=20, help="Number of messages to capture")
    parser.add_argument("--out-csv", default=None, help="CSV path for odometry mode")
    args = parser.parse_args()
    asyncio.run(main_async(args.mode, args.count, Path(args.out_csv) if args.out_csv else None))


if __name__ == "__main__":
    main()
