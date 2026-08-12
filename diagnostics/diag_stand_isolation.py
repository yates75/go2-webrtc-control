"""One-shot diagnostic: test balance_stand and stand_up in ISOLATION as the
sole precondition for a Move command, to find out which one (if either)
actually leaves the robot in a walk-capable state on its own.

Sequence, all in one connection:
  1. sit (reset to a known posture)
  2. balance_stand alone -> one Move -> check state/watch the robot
  3. sit (reset again)
  4. stand_up alone -> one Move -> check state/watch the robot

Usage:
    python diagnostics/diag_stand_isolation.py
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
        result["error_code"] = payload.get("error_code")
        done.set()

    topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]
    for topic in topics:
        conn.datachannel.pub_sub.subscribe(topic, on_message)
    try:
        await asyncio.wait_for(done.wait(), timeout=10.0)
        print(f"  [{label}] {result}")
    except asyncio.TimeoutError:
        print(f"  [{label}] no state message received")
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
        print("=== reset: sit ===")
        await send(conn, 1009)
        await asyncio.sleep(2.5)
        await print_state(conn, "after sit")

        print("\n=== TEST A: balance_stand ALONE, then Move ===")
        print("Watch the robot now.")
        await send(conn, 1002)
        await asyncio.sleep(2.0)
        await print_state(conn, "after balance_stand")
        await send(conn, 1008, {"x": 0.15, "y": 0.0, "z": 0.0})
        await asyncio.sleep(1.5)
        await print_state(conn, "after Move (test A)")
        await send(conn, 1003)
        await asyncio.sleep(1.0)

        print("\n=== reset: sit ===")
        await send(conn, 1009)
        await asyncio.sleep(2.5)
        await print_state(conn, "after sit")

        print("\n=== TEST B: stand_up ALONE, then Move ===")
        print("Watch the robot now.")
        await send(conn, 1004)
        await asyncio.sleep(2.0)
        await print_state(conn, "after stand_up")
        await send(conn, 1008, {"x": 0.15, "y": 0.0, "z": 0.0})
        await asyncio.sleep(1.5)
        await print_state(conn, "after Move (test B)")
        await send(conn, 1003)
    finally:
        await conn.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
