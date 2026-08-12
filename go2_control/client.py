"""Reusable async helpers for the Unitree Go2 Pro WebRTC sport API.

The helper focuses on the JSON framing you described and keeps motion
commands conservative for the Lion Cub shell.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

try:
    from go2_webrtc_driver.go2_webrtc_connection import (
        Go2WebRTCConnection,
        WebRTCConnectionMethod,
    )
except ModuleNotFoundError:
    # Newer go2-webrtc-connect exposes these from webrtc_driver.
    from go2_webrtc_driver.webrtc_driver import (
        Go2WebRTCConnection,
        WebRTCConnectionMethod,
    )

from go2_webrtc_driver.constants import RTC_TOPIC

from .config import Go2Config


MAX_SAFE_WALK_SPEED_MPS = 0.3
SAFE_ACROBATIC_API_IDS = {1025, 1026, 1027}


@dataclass(slots=True)
class SportCommand:
    """Represent one sport API request."""

    api_id: int
    params: Optional[dict[str, Any]] = None


class Go2ControlClient:
    """Async wrapper around a Go2 WebRTC data channel.

    The class keeps the JSON request format in one place so the rest of your
    code can just call intent-based methods such as `stand_up()` or `move()`.
    """

    def __init__(self, connection_method: WebRTCConnectionMethod = WebRTCConnectionMethod.LocalAP) -> None:
        self.connection_method = connection_method
        self.conn: Go2WebRTCConnection | None = None
        self.config = Go2Config()

    def set_config(self, config: Go2Config) -> None:
        """Apply user configuration to the client."""

        self.config = config

    async def _maybe_await(self, value: Any) -> Any:
        """Await coroutine results and pass through regular return values."""

        if asyncio.iscoroutine(value):
            return await value
        return value

    async def connect(self) -> None:
        """Create and connect the WebRTC session."""

        connection_kwargs: dict[str, Any] = {}
        if self.connection_method in (WebRTCConnectionMethod.LocalSTA, WebRTCConnectionMethod.Remote):
            # STA/Remote modes require an explicit target address.
            connection_kwargs["ip"] = self.config.robot_ip

        self.conn = Go2WebRTCConnection(self.connection_method, **connection_kwargs)
        await self._maybe_await(self.conn.connect())

    async def disconnect(self) -> None:
        """Close the WebRTC session if one is open."""

        if self.conn is None:
            return

        disconnect = getattr(self.conn, "disconnect", None)
        if callable(disconnect):
            await self._maybe_await(disconnect())

        self.conn = None

    async def send_command(self, api_id: int, params: Optional[dict[str, Any]] = None) -> None:
        """Send one sport command using the JSON envelope you described."""

        if self.conn is None:
            raise RuntimeError("Call connect() before sending commands.")

        if api_id in SAFE_ACROBATIC_API_IDS:
            raise ValueError(f"API {api_id} is disabled for shell safety.")

        await self.conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], {"api_id": api_id, "parameter": params or {}}
        )

    async def balance_stand(self) -> None:
        await self.send_command(1002)

    async def stop_move(self) -> None:
        await self.send_command(1003)

    async def stand_up(self) -> None:
        await self.send_command(1004)

    async def stand_down(self) -> None:
        await self.send_command(1005)

    async def recovery_stand(self) -> None:
        await self.send_command(1006)

    async def euler_body_tilt(self, roll_radians: float, pitch_radians: float, yaw_radians: float) -> None:
        await self.send_command(1007, {"x": roll_radians, "y": pitch_radians, "z": yaw_radians})

    async def move(self, forward_mps: float, sideways_mps: float = 0.0, turn_rps: float = 0.0) -> None:
        """Send a walking command with a built-in safety cap.

        The robot expects this command to be sent repeatedly in a loop while it
        should keep moving.
        """

        if abs(forward_mps) > MAX_SAFE_WALK_SPEED_MPS:
            raise ValueError(f"forward_mps must be <= {MAX_SAFE_WALK_SPEED_MPS} for shell safety.")

        if abs(sideways_mps) > MAX_SAFE_WALK_SPEED_MPS:
            raise ValueError(f"sideways_mps must be <= {MAX_SAFE_WALK_SPEED_MPS} for shell safety.")

        if abs(turn_rps) > 1.0:
            raise ValueError("turn_rps is capped at 1.0 for conservative control.")

        await self.send_command(1008, {"x": forward_mps, "y": sideways_mps, "z": turn_rps})

    async def move_default(self, sideways_mps: float = 0.0, turn_rps: float = 0.0) -> None:
        """Walk using the configured default speed."""

        await self.move(self.config.default_walk_speed_mps, sideways_mps=sideways_mps, turn_rps=turn_rps)

    async def walk_for(
        self,
        forward_mps: float,
        duration_s: float,
        sideways_mps: float = 0.0,
        turn_rps: float = 0.0,
        interval_s: float = 0.1,
    ) -> None:
        """Walk for a short, bounded time and stop automatically.

        This sends the move command in a loop because the sport API expects
        repeated updates while the robot should keep walking.
        """

        if duration_s <= 0:
            raise ValueError("duration_s must be greater than 0.")

        if interval_s <= 0:
            raise ValueError("interval_s must be greater than 0.")

        end_time = asyncio.get_running_loop().time() + duration_s

        try:
            while asyncio.get_running_loop().time() < end_time:
                await self.move(forward_mps, sideways_mps=sideways_mps, turn_rps=turn_rps)
                await asyncio.sleep(interval_s)
        finally:
            await self.stop_move()

    async def walk_for_default(
        self,
        duration_s: float,
        sideways_mps: float = 0.0,
        turn_rps: float = 0.0,
        interval_s: float = 0.1,
    ) -> None:
        """Walk for a short time using the configured default speed."""

        await self.walk_for(
            self.config.default_walk_speed_mps,
            duration_s,
            sideways_mps=sideways_mps,
            turn_rps=turn_rps,
            interval_s=interval_s,
        )

    async def sit(self) -> None:
        await self.send_command(1009)

    async def rise_sit(self) -> None:
        await self.send_command(1010)

    async def speed_level(self, level: int) -> None:
        if level not in (0, 1, 2):
            raise ValueError("speed level must be 0, 1, or 2.")
        await self.send_command(1015, {"data": level})

    async def hello(self) -> None:
        await self.send_command(1016)

    async def stretch(self) -> None:
        await self.send_command(1017)

    async def content(self) -> None:
        await self.send_command(1020)

    async def heart_pose(self) -> None:
        await self.send_command(1036)

    async def dance1(self) -> None:
        await self.send_command(1022)

    async def dance2(self) -> None:
        await self.send_command(1023)

    async def wallow(self) -> None:
        await self.send_command(1021)

    async def scrape(self) -> None:
        await self.send_command(1029)

    async def wiggle_hips(self) -> None:
        await self.send_command(1033)

    async def pose(self, enable: bool = True) -> None:
        """Enable/disable manual pose mode (body tilt via app-style controls)."""

        await self.send_command(1028, {"data": enable})

    async def switch_gait(self, gait_id: int) -> None:
        """Select a gait pattern. Valid IDs depend on firmware."""

        await self.send_command(1011, {"data": gait_id})

    async def set_body_height(self, height_m: float) -> None:
        """Adjust standing body height, same {"data": value} shape as speed_level()."""

        await self.send_command(1013, {"data": height_m})

    async def set_foot_raise_height(self, height_m: float) -> None:
        """Adjust foot swing height while walking, same shape as speed_level()."""

        await self.send_command(1014, {"data": height_m})
