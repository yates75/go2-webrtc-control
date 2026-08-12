"""List and play built-in sounds through the Go2's onboard speaker.

Uses the driver's generic `publish_request_new` helper against the audio
hub topic, with the documented `AUDIO_API` ids from
`go2_webrtc_driver.constants`. The `list` action's response shape (in
particular, the field name and type used to identify a track) hasn't been
confirmed against real hardware -- run `list` first and adjust `play
--id` to match whatever key it actually returns.

Usage:
    python -m go2_control.audio list
    python -m go2_control.audio play --id 1
"""

from __future__ import annotations

import argparse
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
from go2_webrtc_driver.constants import AUDIO_API, RTC_TOPIC


async def get_audio_list(conn: Go2WebRTCConnection) -> dict:
    """Ask the robot for its list of built-in/uploaded sounds."""

    return await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["AUDIO_HUB_REQ"],
        {"api_id": AUDIO_API["GET_AUDIO_LIST"]},
    )


async def play_audio(conn: Go2WebRTCConnection, audio_id: str) -> dict:
    """Start playing a sound by id (see `get_audio_list` for valid ids)."""

    return await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["AUDIO_HUB_REQ"],
        {"api_id": AUDIO_API["SELECT_START_PLAY"], "parameter": {"id": audio_id}},
    )


async def main_async(action: str, audio_id: str | None) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        if action == "list":
            print(await get_audio_list(conn))
        else:
            if not audio_id:
                raise SystemExit("play requires --id <audio_id> (see `list` output)")
            print(await play_audio(conn, audio_id))
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="List or play sounds on the Go2's speaker")
    parser.add_argument("action", choices=["list", "play"])
    parser.add_argument("--id", dest="audio_id", default=None, help="Audio id to play (from `list`)")
    args = parser.parse_args()
    asyncio.run(main_async(args.action, args.audio_id))


if __name__ == "__main__":
    main()
