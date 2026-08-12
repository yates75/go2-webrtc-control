"""One-shot diagnostic: check the robot's current motion_switcher mode
(normal vs ai/mcf). Read-only -- no movement command is sent.

Sourced from legion1581/unitree_webrtc_connect's sportmode.py example:
  GET current mode:  MOTION_SWITCHER api_id 1001

Usage:
    python diagnostics/diag_motion_mode.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

from go2_webrtc_driver.constants import RTC_TOPIC


async def main_async() -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        response = await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], {"api_id": 1001}
        )
        print(f"raw response: {response}")
        status = response.get("data", {}).get("header", {}).get("status", {})
        if status.get("code") == 0:
            raw_data = response.get("data", {}).get("data", "")
            data = json.loads(raw_data) if raw_data else {}
            print(f"Current motion mode: {data.get('name')}")
        else:
            print(f"Request failed: status={status}")
    finally:
        await conn.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
