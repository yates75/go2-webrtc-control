"""Quest 3S bridge server for Go2 control + VR camera relay.

Run:
    python -m go2_control.vr_bridge

Then open on Quest Browser:
    http://<MAC_IP>:8765/vr/index.html
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .client import Go2ControlClient
from .vr_webrtc import Go2WebRTCRelay, WebRTCOffer

HOST = "0.0.0.0"
PORT = 8765

CONTROL_HZ = 12.0
DEADMAN_TIMEOUT_S = 0.25
MAX_FORWARD_MPS = 0.3
MAX_TURN_RPS = 0.7


@dataclass(slots=True)
class ControlState:
    forward_mps: float = 0.0
    turn_rps: float = 0.0
    connected: bool = False
    last_input_ts: float = 0.0


class QuestGo2Bridge:
    """Own the Go2 client, control loop, and WebRTC relay state."""

    def __init__(self) -> None:
        self.client = Go2ControlClient()
        self.relay = Go2WebRTCRelay(self.client)
        self.state = ControlState()
        self.lock = asyncio.Lock()
        self.control_task: asyncio.Task | None = None

    async def startup(self) -> None:
        await self.client.connect()
        async with self.lock:
            self.state.last_input_ts = time.monotonic()
            self.state.connected = False
        self.control_task = asyncio.create_task(self._control_loop())

    async def shutdown(self) -> None:
        if self.control_task is not None:
            self.control_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.control_task

        with contextlib.suppress(Exception):
            await self.client.stop_move()
        with contextlib.suppress(Exception):
            await self.client.sit()
        with contextlib.suppress(Exception):
            await self.relay.close_all()

        await self.client.disconnect()

    async def _control_loop(self) -> None:
        """Send conservative movement commands at a fixed rate."""

        interval = 1.0 / CONTROL_HZ
        sent_stop_last = False

        while True:
            async with self.lock:
                age = time.monotonic() - self.state.last_input_ts
                connected = self.state.connected
                forward = self.state.forward_mps
                turn = self.state.turn_rps

            stale = age > DEADMAN_TIMEOUT_S
            must_stop = stale or not connected

            if must_stop:
                if not sent_stop_last:
                    with contextlib.suppress(Exception):
                        await self.client.stop_move()
                    sent_stop_last = True
            else:
                with contextlib.suppress(Exception):
                    await self.client.move(forward, turn_rps=turn)
                sent_stop_last = False

            await asyncio.sleep(interval)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    async def handle_ws_message(self, payload: dict) -> dict:
        msg_type = payload.get("type", "")

        if msg_type in {"heartbeat", "twist"}:
            async with self.lock:
                self.state.last_input_ts = time.monotonic()

        if msg_type == "twist":
            vx = float(payload.get("vx", 0.0))
            wz = float(payload.get("wz", 0.0))

            vx = self._clamp(vx, -MAX_FORWARD_MPS, MAX_FORWARD_MPS)
            wz = self._clamp(wz, -MAX_TURN_RPS, MAX_TURN_RPS)

            async with self.lock:
                self.state.forward_mps = vx
                self.state.turn_rps = wz

            return {"ok": True, "type": "twist", "vx": vx, "wz": wz}

        if msg_type == "action":
            name = str(payload.get("name", "")).strip().lower()
            if name == "stand_up":
                await self.client.stand_up()
            elif name == "sit":
                await self.client.sit()
            elif name == "stop":
                await self.client.stop_move()
            elif name == "hello":
                await self.client.hello()
            elif name == "content":
                await self.client.content()
            elif name == "balance_stand":
                await self.client.balance_stand()
            else:
                return {"ok": False, "error": f"unknown action: {name}"}

            return {"ok": True, "type": "action", "name": name}

        if msg_type == "heartbeat":
            return {"ok": True, "type": "heartbeat"}

        return {"ok": False, "error": f"unsupported message type: {msg_type}"}


bridge = QuestGo2Bridge()
app = FastAPI(title="Quest-Go2 Bridge", version="0.1.0")


@app.on_event("startup")
async def _startup() -> None:
    await bridge.startup()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await bridge.shutdown()


@app.get("/health")
async def health() -> JSONResponse:
    async with bridge.lock:
        age = time.monotonic() - bridge.state.last_input_ts
        payload = {
            "ok": True,
            "control_connected": bridge.state.connected,
            "last_input_age_s": round(age, 3),
            "deadman_timeout_s": DEADMAN_TIMEOUT_S,
        }
    return JSONResponse(payload)


@app.post("/api/webrtc/offer")
async def webrtc_offer(offer: WebRTCOffer) -> JSONResponse:
    answer = await bridge.relay.create_answer(offer)
    return JSONResponse(answer)


@app.websocket("/ws/control")
async def control_ws(websocket: WebSocket) -> None:
    await websocket.accept()

    async with bridge.lock:
        bridge.state.connected = True
        bridge.state.last_input_ts = time.monotonic()

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            result = await bridge.handle_ws_message(payload)
            await websocket.send_text(json.dumps(result))
    except WebSocketDisconnect:
        pass
    finally:
        async with bridge.lock:
            bridge.state.connected = False
            bridge.state.forward_mps = 0.0
            bridge.state.turn_rps = 0.0
        with contextlib.suppress(Exception):
            await bridge.client.stop_move()


STATIC_DIR = Path(__file__).resolve().parent / "vr_static"
app.mount("/vr", StaticFiles(directory=STATIC_DIR, html=True), name="vr")


def main() -> None:
    import uvicorn

    uvicorn.run("go2_control.vr_bridge:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    main()
