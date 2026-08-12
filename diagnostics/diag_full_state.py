"""One-shot diagnostic: print the FULL raw sportmodestate payload.

telemetry.py only prints a few summarized fields (position/velocity/rpy).
This prints every key in the raw message so we can see fields like
"mode" or "gait_type" that might explain why Move commands are being
accepted (status.code == 0) but not producing visible motion.

Usage:
    python diagnostics/diag_full_state.py
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


async def main_async() -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    await conn.datachannel.disableTrafficSaving(True)

    done = asyncio.Event()

    def on_message(message: dict) -> None:
        payload = _unwrap(message)
        print(f"topic={message.get('topic')}")
        for key, value in payload.items():
            print(f"  {key}: {value!r}")
        done.set()

    topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]
    for topic in topics:
        conn.datachannel.pub_sub.subscribe(topic, on_message)

    try:
        await asyncio.wait_for(done.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        print("No state message received in 15s.")
    finally:
        for topic in topics:
            conn.datachannel.pub_sub.unsubscribe(topic)
        await conn.disconnect()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
