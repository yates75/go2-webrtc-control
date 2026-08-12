"""Standalone script to subscribe to the Go2's LIDAR point-cloud feed.

The exact shape of the decoded payload depends on the bundled WASM voxel
decoder and hasn't been verified against real hardware in this repo yet.
Run this once with a robot connected and inspect the printed payload
before relying on its structure in your own code.

Usage:
    python -m go2_control.lidar_view
    python -m go2_control.lidar_view --count 50
    python -m go2_control.lidar_view --record --out-dir lidar_recording
"""

from __future__ import annotations

import argparse
import asyncio
import pickle
import sys
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


async def stream_lidar(conn: Go2WebRTCConnection, count: int, out_dir: Path | None = None) -> None:
    """Enable the LIDAR sensor, print `count` decoded messages, then turn it back off.

    If `out_dir` is given, each raw decoded payload is pickled to
    `out_dir/frame_NNN.pkl` so it can be reloaded later for analysis or
    point-cloud visualization, without assuming a fixed payload schema.
    """

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)

    received = 0
    done = asyncio.Event()

    def on_message(message: dict) -> None:
        nonlocal received
        payload = message["data"]["data"]
        if isinstance(payload, dict):
            print(f"[{received}] lidar message keys: {list(payload.keys())}")
        else:
            print(f"[{received}] lidar message type: {type(payload)}")

        if out_dir is not None:
            frame_path = out_dir / f"frame_{received:04d}.pkl"
            with frame_path.open("wb") as handle:
                pickle.dump(payload, handle)

        received += 1
        if received >= count:
            done.set()

    # Full-resolution point data is only sent once traffic saving is disabled.
    await conn.datachannel.disableTrafficSaving(True)
    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["ULIDAR_ARRAY"], on_message)
    conn.datachannel.pub_sub.publish_without_callback(RTC_TOPIC["ULIDAR_SWITCH"], "on")

    try:
        await asyncio.wait_for(done.wait(), timeout=30.0)
    except asyncio.TimeoutError:
        print(f"Only received {received}/{count} lidar messages in 30s -- stopping.")
    finally:
        conn.datachannel.pub_sub.unsubscribe(RTC_TOPIC["ULIDAR_ARRAY"])
        conn.datachannel.pub_sub.publish_without_callback(RTC_TOPIC["ULIDAR_SWITCH"], "off")


async def main_async(count: int, out_dir: Path | None) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await stream_lidar(conn, count, out_dir=out_dir)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream decoded LIDAR point-cloud messages from the Go2")
    parser.add_argument("--count", type=int, default=20, help="Number of messages to print before stopping")
    parser.add_argument("--record", action="store_true", help="Save each decoded frame to --out-dir")
    parser.add_argument("--out-dir", default="lidar_recording", help="Directory for recorded frames")
    args = parser.parse_args()
    asyncio.run(main_async(args.count, Path(args.out_dir) if args.record else None))


if __name__ == "__main__":
    main()
