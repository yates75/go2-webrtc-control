"""One-shot test: disable obstacle avoidance, attempt a short slow walk,
then re-enable obstacle avoidance immediately afterward.

Safety: obstacle avoidance is what makes the robot auto-stop before
hitting something. This script disables it only for the few seconds of
the walk test and re-enables it in a `finally` block so it's restored
even if something goes wrong. Only run this with clear space ahead of
the robot and a person positioned to the side (not in its path), ready
to Ctrl-C.

Usage:
    python diagnostics/diag_obstacle_toggle_test.py
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

from go2_control.client import Go2ControlClient
from go2_control.experimental import get_obstacle_avoidance, set_obstacle_avoidance


async def main_async() -> None:
    client = Go2ControlClient(WebRTCConnectionMethod.LocalAP)
    await client.connect()
    conn = client.conn
    try:
        before = await get_obstacle_avoidance(conn)
        print(f"Obstacle avoidance before: {before}")

        print("Disabling obstacle avoidance...")
        await set_obstacle_avoidance(conn, False)
        after_disable = await get_obstacle_avoidance(conn)
        print(f"Obstacle avoidance after disable call: {after_disable}")

        try:
            print("sit (reset)...")
            await client.sit()
            await asyncio.sleep(2.5)

            print("stand_up...")
            await client.stand_up()
            await asyncio.sleep(1.5)

            print("Walking forward at 0.1 m/s for 1.5s -- watch the robot now.")
            await client.walk_for(0.1, duration_s=1.5, interval_s=0.1)
        finally:
            print("Re-enabling obstacle avoidance...")
            await set_obstacle_avoidance(conn, True)
            after_enable = await get_obstacle_avoidance(conn)
            print(f"Obstacle avoidance after re-enable: {after_enable}")
    finally:
        await client.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
