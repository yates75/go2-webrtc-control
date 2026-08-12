"""One-shot test: drive the robot by publishing simulated joystick input
to rt/wirelesscontroller, bypassing the sport-API Move command entirely.

This is the same channel the robot's real physical remote uses, sourced
from legion1581/unitree_webrtc_connect's obstacles_avoid.py example.
If Move (api_id 1008) doesn't work in this robot's "mcf" motion mode
but this does, that tells us the fix belongs at this layer instead.

Usage:
    python diagnostics/diag_joystick_drive.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

from go2_webrtc_driver.constants import RTC_TOPIC

from go2_control.client import Go2ControlClient


def publish_wireless_controller(pub_sub, lx=0.0, ly=0.0, rx=0.0, ry=0.0, keys=0) -> None:
    pub_sub.publish_without_callback(
        RTC_TOPIC["WIRELESS_CONTROLLER"],
        {"lx": lx, "ly": ly, "rx": rx, "ry": ry, "keys": keys},
    )


async def main_async() -> None:
    client = Go2ControlClient(WebRTCConnectionMethod.LocalAP)
    await client.connect()
    conn = client.conn
    try:
        print("sit (reset)...")
        await client.sit()
        await asyncio.sleep(2.5)

        print("stand_up...")
        await client.stand_up()
        await asyncio.sleep(1.5)

        print("Driving forward via wirelesscontroller (ly=0.5) for 2s -- watch the robot now.")
        t = 0.0
        while t < 2.0:
            publish_wireless_controller(conn.datachannel.pub_sub, ly=0.5)
            await asyncio.sleep(0.02)
            t += 0.02
        publish_wireless_controller(conn.datachannel.pub_sub)  # stop
        print("Stopped.")
    finally:
        await client.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
