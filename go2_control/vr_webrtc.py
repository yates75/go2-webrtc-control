"""WebRTC relay helpers for Quest <-> Go2 video streaming.

This v1 module accepts a browser offer and returns an answer with a single
video track. If a native Go2 video track is not available yet, it serves a
synthetic fallback track so the Quest pipeline can still be tested end-to-end.
"""

from __future__ import annotations

import asyncio
import contextlib
import math
import time
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

import av
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from pydantic import BaseModel


class WebRTCOffer(BaseModel):
    sdp: str
    type: str


class FallbackStatusVideoTrack(VideoStreamTrack):
    """Simple generated track so Quest rendering can be validated without Go2 video."""

    def __init__(self) -> None:
        super().__init__()
        self._start = time.monotonic()
        self._frame_index = 0

    async def recv(self) -> av.VideoFrame:
        pts, time_base = await self.next_timestamp()

        width = 960
        height = 540
        frame = av.VideoFrame(width=width, height=height, format="rgb24")
        img = frame.to_ndarray()

        t = time.monotonic() - self._start
        pulse = (math.sin(t * 2.0) + 1.0) * 0.5

        img[:, :, 0] = int(20 + 60 * pulse)
        img[:, :, 1] = int(90 + 90 * pulse)
        img[:, :, 2] = int(140 + 80 * (1.0 - pulse))

        bar_w = width // 12
        for i in range(0, width, bar_w * 2):
            img[:, i : i + bar_w, :] = [220, 180, 40]

        title_h = 60
        img[:title_h, :, :] = [30, 30, 30]

        # Moving stripe helps verify low-latency updates in-headset.
        stripe_x = (self._frame_index * 8) % width
        img[title_h:height, stripe_x : stripe_x + 12, :] = [245, 245, 245]

        self._frame_index += 1

        frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        frame.pts = pts
        frame.time_base = time_base if time_base else Fraction(1, 90000)
        return frame


@dataclass(slots=True)
class Go2WebRTCRelay:
    """Manage browser peer connections for VR video viewing."""

    go2_client: Any
    peers: set[RTCPeerConnection] = field(default_factory=set)

    def _try_get_go2_video_track(self) -> VideoStreamTrack | None:
        """Try common attribute paths used by Go2/WebRTC libraries.

        The exact path can vary by driver version, so we probe defensively.
        """

        conn = getattr(self.go2_client, "conn", None)
        if conn is None:
            return None

        candidates = [
            ("video",),
            ("video_track",),
            ("webrtc_video", "video_track"),
            ("video_channel", "track"),
            ("video_channel", "video_track"),
        ]

        for path in candidates:
            value: Any = conn
            for part in path:
                value = getattr(value, part, None)
                if value is None:
                    break
            if isinstance(value, VideoStreamTrack):
                return value

        return None

    async def create_answer(self, offer: WebRTCOffer) -> dict[str, str]:
        """Create a WebRTC answer for a Quest/browser peer."""

        pc = RTCPeerConnection()
        self.peers.add(pc)

        @pc.on("connectionstatechange")
        async def _on_state_change() -> None:
            if pc.connectionState in {"failed", "closed", "disconnected"}:
                await self._close_peer(pc)

        video_track = self._try_get_go2_video_track() or FallbackStatusVideoTrack()
        pc.addTrack(video_track)

        await pc.setRemoteDescription(RTCSessionDescription(sdp=offer.sdp, type=offer.type))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }

    async def _close_peer(self, pc: RTCPeerConnection) -> None:
        if pc in self.peers:
            self.peers.remove(pc)
        with contextlib.suppress(Exception):
            await pc.close()

    async def close_all(self) -> None:
        tasks = [self._close_peer(pc) for pc in list(self.peers)]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
