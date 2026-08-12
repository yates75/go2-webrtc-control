"""Switch motion mode from 'mcf' to 'normal', then test a short walk.

Sourced from legion1581/unitree_webrtc_connect's sportmode.py example:
  GET mode:    MOTION_SWITCHER api_id 1001
  SET mode:    MOTION_SWITCHER api_id 1002, parameter {"name": "normal"}

Usage:
    python diagnostics/diag_switch_normal_and_walk.py
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

from go2_control.client import Go2ControlClient


async def get_mode(conn: Go2WebRTCConnection) -> str | None:
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["MOTION_SWITCHER"], {"api_id": 1001}
    )
    status = response.get("data", {}).get("header", {}).get("status", {})
    if status.get("code") != 0:
        print(f"  get_mode failed: status={status}")
        return None
    raw_data = response.get("data", {}).get("data", "")
    data = json.loads(raw_data) if raw_data else {}
    return data.get("name")


async def main_async() -> None:
    client = Go2ControlClient(WebRTCConnectionMethod.LocalAP)
    await client.connect()
    conn = client.conn
    try:
        mode = await get_mode(conn)
        print(f"Mode before: {mode}")

        if mode not in ("normal", "sport_mode"):
            for candidate in ("sport_mode", "normal"):
                print(f"Trying to select mode name={candidate!r} -- watch the robot...")
                switch_response = await conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["MOTION_SWITCHER"],
                    {"api_id": 1002, "parameter": {"form": "0", "name": candidate}},
                )
                switch_status = switch_response.get("data", {}).get("header", {}).get("status", {})
                print(f"  select({candidate!r}) status: {switch_status}")
                if switch_status.get("code") == 0:
                    await asyncio.sleep(6.0)
                    mode = await get_mode(conn)
                    print(f"Mode after switch: {mode}")
                    break

        print("sit (reset)...")
        await client.sit()
        await asyncio.sleep(2.5)

        print("stand_up...")
        await client.stand_up()
        await asyncio.sleep(1.5)

        print("Walking forward at 0.1 m/s for 2s -- watch the robot now.")
        await client.walk_for(0.1, duration_s=2.0, interval_s=0.1)
    finally:
        await client.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
