"""VUI (LED/volume/brightness) and obstacle-avoidance control, plus honest
notes on what this project genuinely cannot reach.

The `api_id` values below for the VUI and obstacle-avoidance topics come
from working example scripts in the actively-maintained
`unitree_webrtc_connect` fork (github.com/legion1581/unitree_webrtc_connect,
examples/go2/data_channel/{vui,obstacles_avoid}) -- unlike a guessed id,
these are sourced from real, working code, so the functions below send
real requests rather than raising `NotImplementedError`.

What is still genuinely out of reach for this project:

- **True EDU-style low-level joint control** (`rt/lowcmd` -- direct
  per-joint q/dq/tau/kp/kd commands bypassing the balance controller).
  The upstream driver only exposes `rt/lf/lowstate` for *reading* motor
  telemetry; there is no example anywhere in that project of *sending*
  `LowCmd` over the WebRTC data channel, and there's a structural reason
  for that: low-level control needs a ~500Hz-1kHz real-time DDS loop,
  which the WebRTC bridge (built for the phone app) isn't designed to
  sustain. Unitree's own low-level SDK (`unitree_sdk2`) talks to that bus
  over wired Ethernet + native DDS, not this bridge. There's no code path
  here to fill in for this -- it would need different hardware wiring and
  a different SDK entirely.
- **SLAM mapping start** (`rt/qt_command`) -- no sourced payload format
  was found for this one, so `start_slam_mapping()` still raises
  `NotImplementedError`. `watch_slam_topics()` remains fully safe to run
  (read-only), in case the robot's onboard SLAM is already active.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection
except ModuleNotFoundError:
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection
from go2_webrtc_driver.constants import RTC_TOPIC, VUI_COLOR

VUI_API = {
    "SET_VOLUME": 1003,
    "GET_VOLUME": 1004,
    "SET_BRIGHTNESS": 1005,
    "GET_BRIGHTNESS": 1006,
    "SET_COLOR": 1007,
}

OBSTACLES_AVOID_API = {
    "SWITCH_SET": 1001,
    "SWITCH_GET": 1002,
}


def _unwrap_response(response: dict) -> tuple[int, dict]:
    """Pull (status_code, parsed_data) out of a request/response envelope."""

    payload = response.get("data", {})
    code = payload.get("header", {}).get("status", {}).get("code", -1)
    raw_data = payload.get("data", "")
    if isinstance(raw_data, str) and raw_data:
        try:
            return code, json.loads(raw_data)
        except json.JSONDecodeError:
            return code, {}
    return code, raw_data if isinstance(raw_data, dict) else {}


async def get_volume(conn: Go2WebRTCConnection) -> int | None:
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["VUI"], {"api_id": VUI_API["GET_VOLUME"]}
    )
    _, data = _unwrap_response(response)
    return data.get("volume")


async def set_volume(conn: Go2WebRTCConnection, volume: int) -> None:
    """Set speaker volume, 0-10."""

    if not 0 <= volume <= 10:
        raise ValueError("volume must be between 0 and 10")
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["VUI"],
        {"api_id": VUI_API["SET_VOLUME"], "parameter": {"volume": volume}},
    )


async def get_brightness(conn: Go2WebRTCConnection) -> int | None:
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["VUI"], {"api_id": VUI_API["GET_BRIGHTNESS"]}
    )
    _, data = _unwrap_response(response)
    return data.get("brightness")


async def set_brightness(conn: Go2WebRTCConnection, brightness: int) -> None:
    """Set status-light brightness, 0-10."""

    if not 0 <= brightness <= 10:
        raise ValueError("brightness must be between 0 and 10")
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["VUI"],
        {"api_id": VUI_API["SET_BRIGHTNESS"], "parameter": {"brightness": brightness}},
    )


async def set_led_color(
    conn: Go2WebRTCConnection,
    color: str,
    time_s: float = 5.0,
    flash_cycle_ms: int | None = None,
) -> None:
    """Set the robot's status LED color for `time_s` seconds.

    `flash_cycle_ms`, if given, makes the LED flash on/off at that period
    (must be between 499 and time_s*1000, per the upstream example).
    """

    valid_colors = [v for k, v in vars(VUI_COLOR).items() if not k.startswith("_")]
    if color not in valid_colors:
        raise ValueError(f"Unknown color {color!r}, expected one of {valid_colors}")

    parameter: dict = {"color": color, "time": time_s}
    if flash_cycle_ms is not None:
        parameter["flash_cycle"] = flash_cycle_ms

    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["VUI"],
        {"api_id": VUI_API["SET_COLOR"], "parameter": parameter},
    )


async def get_obstacle_avoidance(conn: Go2WebRTCConnection) -> bool | None:
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["OBSTACLES_AVOID"], {"api_id": OBSTACLES_AVOID_API["SWITCH_GET"]}
    )
    _, data = _unwrap_response(response)
    return data.get("enable")


async def set_obstacle_avoidance(conn: Go2WebRTCConnection, enabled: bool) -> None:
    """Toggle the robot's built-in obstacle avoidance."""

    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["OBSTACLES_AVOID"],
        {"api_id": OBSTACLES_AVOID_API["SWITCH_SET"], "parameter": {"enable": enabled}},
    )


async def start_slam_mapping(conn: Go2WebRTCConnection) -> None:
    """Trigger onboard SLAM mapping mode. NOT IMPLEMENTED -- see module docstring."""

    raise NotImplementedError(
        f"No sourced payload format for {RTC_TOPIC['SLAM_QT_COMMAND']} was found. "
        "Find a verified command shape (not a guess) before sending a real request."
    )


async def watch_slam_topics(conn: Go2WebRTCConnection, count: int = 10) -> None:
    """Read-only: print raw messages from the SLAM cloud-point and odometry topics, if any arrive.

    Safe to run any time -- this only listens. If the robot's onboard SLAM
    stack isn't already active (e.g. started from the Unitree app), you
    may see nothing at all, which is expected and not an error.
    """

    received = 0
    done = asyncio.Event()

    def on_message(message: dict) -> None:
        nonlocal received
        print(f"[{received}] topic={message.get('topic')} data={message.get('data')}")
        received += 1
        if received >= count:
            done.set()

    await conn.datachannel.disableTrafficSaving(True)
    topics = [RTC_TOPIC["LIDAR_MAPPING_CLOUD_POINT"], RTC_TOPIC["LIDAR_MAPPING_ODOM"]]
    for topic in topics:
        conn.datachannel.pub_sub.subscribe(topic, on_message)

    try:
        await asyncio.wait_for(done.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        print("No SLAM messages received in 15s -- onboard SLAM is likely not active.")
    finally:
        for topic in topics:
            conn.datachannel.pub_sub.unsubscribe(topic)
