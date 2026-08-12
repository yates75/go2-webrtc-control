"""Standalone script to view or save frames from the Go2's front camera.

Usage:
    python -m go2_control.camera_view              # save 10 JPEG snapshots
    python -m go2_control.camera_view --live        # live cv2 preview window (needs opencv-python)
    python -m go2_control.camera_view --count 30 --interval 0.5
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


async def stream_camera(conn: Go2WebRTCConnection, on_frame) -> None:
    """Register a frame callback and turn the video channel on.

    The Go2 only starts sending RTP frames once the video channel is
    switched on, so the callback must be registered first or the very
    first frame (which unblocks the driver's internal track handler)
    is never delivered to it.
    """

    async def _handle_track(track) -> None:
        while True:
            frame = await track.recv()
            await on_frame(frame)

    conn.video.add_track_callback(_handle_track)
    conn.video.switchVideoChannel(True)


async def capture_snapshots(conn: Go2WebRTCConnection, out_dir: Path, count: int, interval_s: float) -> None:
    """Save `count` JPEG snapshots spaced `interval_s` apart, using an already-connected `conn`."""

    out_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    done = asyncio.Event()

    async def on_frame(frame) -> None:
        nonlocal saved
        if saved >= count:
            return
        image_path = out_dir / f"frame_{saved:03d}.jpg"
        frame.to_image().save(image_path)
        print(f"Saved {image_path}")
        saved += 1
        if saved >= count:
            done.set()
        else:
            await asyncio.sleep(interval_s)

    await stream_camera(conn, on_frame)
    await done.wait()


async def save_snapshots(out_dir: Path, count: int, interval_s: float) -> None:
    """Connect, save `count` JPEG snapshots spaced `interval_s` apart, then disconnect."""

    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await capture_snapshots(conn, out_dir, count, interval_s)
    finally:
        await conn.disconnect()


async def live_preview(count: int) -> None:
    """Connect and show frames in a cv2 window until `count` frames or 'q' is pressed."""

    import cv2

    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    shown = 0
    done = asyncio.Event()

    async def on_frame(frame) -> None:
        nonlocal shown
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("Go2 camera", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            done.set()
        shown += 1
        if shown >= count:
            done.set()

    await conn.connect()
    try:
        await stream_camera(conn, on_frame)
        await done.wait()
    finally:
        cv2.destroyAllWindows()
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="View or save frames from the Go2 camera")
    parser.add_argument("--live", action="store_true", help="Show a live cv2 preview instead of saving files")
    parser.add_argument("--count", type=int, default=10, help="Number of frames to capture")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between saved snapshots")
    parser.add_argument("--out-dir", default="camera_snapshots", help="Snapshot output directory")
    args = parser.parse_args()

    if args.live:
        asyncio.run(live_preview(args.count))
    else:
        asyncio.run(save_snapshots(Path(args.out_dir), args.count, args.interval))


if __name__ == "__main__":
    main()
