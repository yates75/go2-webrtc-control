"""One-shot diagnostic: check whether obstacle avoidance is enabled.

Read-only -- does not send any movement command. If obstacle avoidance
is on and something (e.g. a person standing close, for supervision) is
in its sensor range, it can silently veto forward translation while
still allowing the robot to lean/shift balance in response to a Move
command -- which matches exactly what we've been seeing.

Usage:
    python diagnostics/diag_obstacle_avoid.py
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

from go2_control.experimental import get_obstacle_avoidance


async def main_async() -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        enabled = await get_obstacle_avoidance(conn)
        print(f"Obstacle avoidance enabled: {enabled}")
    finally:
        await conn.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
