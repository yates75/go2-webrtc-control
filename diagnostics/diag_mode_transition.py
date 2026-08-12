"""One-shot diagnostic: watch the sportmodestate 'mode' field react (or not)
to balance_stand / stand_up / a single Move command, all in one connection.

mode meanings (from Unitree's SportModeState schema):
  0 idle/default-stand   1 balanceStand   3 locomotion   7 damping   8 recoveryStand

Usage:
    python diagnostics/diag_mode_transition.py
"""

from __future__ import annotations

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


def _unwrap(message: dict) -> dict:
    data = message.get("data", {})
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        return data["data"]
    return data if isinstance(data, dict) else {}


async def print_state(conn: Go2WebRTCConnection, label: str) -> None:
    done = asyncio.Event()
    result = {}

    def on_message(message: dict) -> None:
        payload = _unwrap(message)
        result["mode"] = payload.get("mode")
        result["gait_type"] = payload.get("gait_type")
        result["foot_force"] = payload.get("foot_force")
        result["progress"] = payload.get("progress")
        result["error_code"] = payload.get("error_code")
        done.set()

    topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]
    for topic in topics:
        conn.datachannel.pub_sub.subscribe(topic, on_message)
    try:
        await asyncio.wait_for(done.wait(), timeout=10.0)
        print(f"[{label}] {result}")
    except asyncio.TimeoutError:
        print(f"[{label}] no state message received")
    finally:
        for topic in topics:
            conn.datachannel.pub_sub.unsubscribe(topic)


async def send(conn: Go2WebRTCConnection, api_id: int, params=None) -> None:
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["SPORT_MOD"], {"api_id": api_id, "parameter": params or {}}
    )
    status = response.get("data", {}).get("header", {}).get("status", {})
    print(f"  sent api_id={api_id} params={params} -> status={status}")


async def main_async() -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    await conn.datachannel.disableTrafficSaving(True)
    try:
        await print_state(conn, "before anything")

        print("sending sit (1009) to force a known starting posture...")
        await send(conn, 1009)
        await asyncio.sleep(2.0)
        await print_state(conn, "after sit")

        print("sending balance_stand (1002)...")
        await send(conn, 1002)
        await asyncio.sleep(1.5)
        await print_state(conn, "after balance_stand")

        print("sending stand_up (1004)...")
        await send(conn, 1004)
        await asyncio.sleep(1.5)
        await print_state(conn, "after stand_up")

        print("sending one Move (1008) x=0.1...")
        await send(conn, 1008, {"x": 0.1, "y": 0.0, "z": 0.0})
        await asyncio.sleep(0.5)
        await print_state(conn, "after one Move")

        print("sending stop_move (1003)...")
        await send(conn, 1003)
    finally:
        await conn.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
