"""Independent safety watchdog: read-only battery/tilt monitoring, decoupled from whatever else is controlling the robot.

Subscribes to sport-state only -- never sends a movement command -- so it
can run on a second device alongside any other script (or the app, or a
human with the physical remote) without interfering, and keeps watching
even if the primary control script crashes. Alerts once per threshold
breach (re-arms once the value recovers) rather than spamming every
message, and can optionally sound the robot's own speaker as an audible
alert.

Usage:
    python -m go2_control.safety_watchdog
    python -m go2_control.safety_watchdog --min-battery 20 --max-tilt-deg 35 --audio-alert
"""

from __future__ import annotations

import argparse
import asyncio
import math
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

from go2_control.audio import play_audio
from go2_control.telemetry import _unwrap

DEFAULT_ALERT_AUDIO_ID = "1"


async def watch(
    conn: Go2WebRTCConnection,
    min_battery: float,
    max_tilt_deg: float,
    duration_s: float,
    audio_alert: bool,
    audio_id: str,
) -> None:
    state_topics = [RTC_TOPIC["SPORT_MOD_STATE"], RTC_TOPIC["LF_SPORT_MOD_STATE"]]
    breached = {"battery": False, "tilt": False}
    checked = 0
    stop = asyncio.Event()

    def on_message(message: dict) -> None:
        nonlocal checked
        payload = _unwrap(message)
        checked += 1

        bms = payload.get("bms_state")
        battery = bms.get("soc") if isinstance(bms, dict) else None
        imu_state = payload.get("imu_state")
        rpy = imu_state.get("rpy") if isinstance(imu_state, dict) else None
        tilt_deg = (
            max(abs(math.degrees(rpy[0])), abs(math.degrees(rpy[1])))
            if isinstance(rpy, list) and len(rpy) >= 2
            else None
        )

        if battery is not None:
            is_low = battery < min_battery
            if is_low and not breached["battery"]:
                print(f"[ALERT] battery low: {battery}% < {min_battery}%")
                if audio_alert:
                    asyncio.ensure_future(play_audio(conn, audio_id))
            breached["battery"] = is_low

        if tilt_deg is not None:
            is_tilted = tilt_deg > max_tilt_deg
            if is_tilted and not breached["tilt"]:
                print(f"[ALERT] tilt exceeded: {tilt_deg:.1f} deg > {max_tilt_deg} deg")
                if audio_alert:
                    asyncio.ensure_future(play_audio(conn, audio_id))
            breached["tilt"] = is_tilted

        if checked % 20 == 0:
            print(f"[ok] checked={checked} battery={battery} tilt_deg={tilt_deg}")

    for topic in state_topics:
        conn.datachannel.pub_sub.subscribe(topic, on_message)

    print(f"Watching battery (>{min_battery}%) and tilt (<{max_tilt_deg} deg) for {duration_s:.0f}s...")
    try:
        await asyncio.wait_for(stop.wait(), timeout=duration_s)
    except asyncio.TimeoutError:
        pass
    finally:
        for topic in state_topics:
            conn.datachannel.pub_sub.unsubscribe(topic)

    print(f"Watchdog stopped after {checked} state messages.")


async def main_async(min_battery: float, max_tilt_deg: float, duration: float, audio_alert: bool, audio_id: str) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await watch(conn, min_battery, max_tilt_deg, duration, audio_alert, audio_id)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent battery/tilt safety watchdog (read-only, sends no movement commands)")
    parser.add_argument("--min-battery", type=float, default=15.0, help="Alert if battery %% drops below this")
    parser.add_argument("--max-tilt-deg", type=float, default=40.0, help="Alert if roll or pitch exceeds this many degrees")
    parser.add_argument("--duration", type=float, default=3600.0, help="Seconds to watch before stopping")
    parser.add_argument("--audio-alert", action="store_true", help="Also play a sound on the robot's speaker when alerting")
    parser.add_argument(
        "--audio-id", default=DEFAULT_ALERT_AUDIO_ID, help="Audio id to play (see `python -m go2_control.audio list`)"
    )
    args = parser.parse_args()

    try:
        asyncio.run(main_async(args.min_battery, args.max_tilt_deg, args.duration, args.audio_alert, args.audio_id))
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
