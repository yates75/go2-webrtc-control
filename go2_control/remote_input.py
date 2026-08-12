"""Read live input from a physical Unitree remote controller paired with the Go2.

Read-only -- this only prints whatever joystick/button state the robot
reports on `rt/wirelesscontroller`. It does not send any commands, so it
is safe to run alongside anything else (including while a human is
driving the robot with the physical remote).

Usage:
    python -m go2_control.remote_input --count 30
"""

from __future__ import annotations

import argparse
import asyncio
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


async def stream_controller(conn: Go2WebRTCConnection, count: int) -> None:
    """Print `count` raw controller-state messages, then stop."""

    received = 0
    done = asyncio.Event()

    def on_message(message: dict) -> None:
        nonlocal received
        print(f"[{received}] {message.get('data')}")
        received += 1
        if received >= count:
            done.set()

    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["WIRELESS_CONTROLLER"], on_message)
    try:
        await asyncio.wait_for(done.wait(), timeout=30.0)
    except asyncio.TimeoutError:
        print(f"Only received {received}/{count} controller messages in 30s -- stopping.")
    finally:
        conn.datachannel.pub_sub.unsubscribe(RTC_TOPIC["WIRELESS_CONTROLLER"])


async def main_async(count: int) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    await conn.datachannel.disableTrafficSaving(True)
    try:
        await stream_controller(conn, count)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Print live physical-remote input reported by the Go2")
    parser.add_argument("--count", type=int, default=30, help="Number of messages to print before stopping")
    args = parser.parse_args()
    asyncio.run(main_async(args.count))


if __name__ == "__main__":
    main()
