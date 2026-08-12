"""Record live rt/wirelesscontroller + rt/(lf/)sportmodestate traffic while
a human drives the robot with the physical Unitree remote (or the app, if
only one WebRTC session is possible at a time -- try the physical remote
first since it uses a separate radio channel and won't conflict with this
script's own connection).

Purely read-only: subscribes only, never sends a movement command. Safe to
run while the robot is being driven by anything else.

Usage:
    python diagnostics/diag_record_remote.py --seconds 20
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

from go2_webrtc_driver.constants import RTC_TOPIC


def _unwrap(message: dict) -> dict:
    data = message.get("data", {})
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        return data["data"]
    return data if isinstance(data, dict) else {}


async def main_async(seconds: float) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    await conn.datachannel.disableTrafficSaving(True)

    start = time.monotonic()

    def make_handler(label: str):
        def on_message(message: dict) -> None:
            payload = _unwrap(message)
            t = time.monotonic() - start
            if label == "controller":
                print(f"[{t:6.2f}s] controller: {payload}")
            else:
                keys = {k: payload.get(k) for k in ("mode", "gait_type", "foot_force", "error_code")}
                print(f"[{t:6.2f}s] state:      {keys}")
        return on_message

    topics = [
        RTC_TOPIC["WIRELESS_CONTROLLER"],
        RTC_TOPIC["SPORT_MOD_STATE"],
        RTC_TOPIC["LF_SPORT_MOD_STATE"],
    ]
    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["WIRELESS_CONTROLLER"], make_handler("controller"))
    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["SPORT_MOD_STATE"], make_handler("state"))
    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["LF_SPORT_MOD_STATE"], make_handler("state"))

    print(f"Recording for {seconds:.0f}s -- drive the robot with the physical remote now.")
    try:
        await asyncio.sleep(seconds)
    finally:
        for topic in topics:
            conn.datachannel.pub_sub.unsubscribe(topic)
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Record wirelesscontroller + sportmodestate traffic")
    parser.add_argument("--seconds", type=float, default=20.0, help="How long to record")
    args = parser.parse_args()
    asyncio.run(main_async(args.seconds))


if __name__ == "__main__":
    main()
