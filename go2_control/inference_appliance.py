"""Headless live object detection -- a standing perception appliance with no display required.

Same detector as `object_tracker.py --live` (YOLO with persistent
tracking IDs) but with no cv2 window, so it can run on a headless SBC
(Raspberry Pi, Jetson) as an always-on perception station independent of
whoever is driving the robot. Detections are logged continuously; an
occasional annotated snapshot (not every frame) is saved so accuracy can
be spot-checked later without a live display.

First run downloads the model weights (~6MB) -- do this once with
internet access before taking the robot somewhere offline.

Usage:
    python -m go2_control.inference_appliance --duration 1800
    python -m go2_control.inference_appliance --target person --save-snapshots --snapshot-every 60
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import time
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

from go2_control.camera_view import stream_camera
from go2_control.object_tracker import _load_model, _tracked_detections


async def run_appliance(
    conn: Go2WebRTCConnection,
    target_class: str | None,
    duration_s: float,
    out_csv: Path,
    snapshot_dir: Path | None,
    snapshot_every_s: float,
) -> None:
    model = _load_model()
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if snapshot_dir is not None:
        snapshot_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    last_snapshot = 0.0
    stop = asyncio.Event()

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["timestamp", "frame", "track_id", "class_name", "confidence", "center_x", "center_y", "box_w", "box_h"]
        )

        async def on_frame(frame) -> None:
            nonlocal processed, last_snapshot
            img = frame.to_ndarray(format="bgr24")
            results, matches = await asyncio.to_thread(_tracked_detections, model, img, target_class)

            timestamp = time.time()
            for match in matches:
                writer.writerow(
                    [
                        timestamp,
                        processed,
                        match["track_id"],
                        match["class_name"],
                        match["confidence"],
                        match["center_x"],
                        match["center_y"],
                        match["box_w"],
                        match["box_h"],
                    ]
                )
            handle.flush()

            if matches:
                print(f"[{processed}] {len(matches)} detection(s): " + ", ".join(m["class_name"] for m in matches))

            if snapshot_dir is not None:
                now = time.monotonic()
                if now - last_snapshot >= snapshot_every_s:
                    last_snapshot = now
                    import cv2

                    annotated = results.plot()
                    cv2.imwrite(str(snapshot_dir / f"snapshot_{processed:05d}.jpg"), annotated)

            processed += 1

        await stream_camera(conn, on_frame)
        print(f"Watching for {duration_s:.0f}s (Ctrl-C to stop early)...")
        try:
            await asyncio.wait_for(stop.wait(), timeout=duration_s)
        except asyncio.TimeoutError:
            pass

    print(f"Processed {processed} frames, logged detections to {out_csv}")


async def main_async(
    target: str | None,
    duration: float,
    out_csv: Path,
    snapshot_dir: Path | None,
    snapshot_every: float,
) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await run_appliance(conn, target, duration, out_csv, snapshot_dir, snapshot_every)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Headless standing object-detection appliance (no display required)")
    parser.add_argument("--target", default=None, help="COCO class to filter to, e.g. person (default: all classes)")
    parser.add_argument("--duration", type=float, default=1800.0, help="Seconds to run before stopping")
    parser.add_argument("--out-csv", default="appliance_detections.csv", help="CSV output path")
    parser.add_argument("--save-snapshots", action="store_true", help="Periodically save annotated JPEGs")
    parser.add_argument("--snapshot-dir", default="appliance_snapshots", help="Directory for periodic snapshots")
    parser.add_argument("--snapshot-every", type=float, default=30.0, help="Seconds between saved snapshots")
    args = parser.parse_args()

    snapshot_dir = Path(args.snapshot_dir) if args.save_snapshots else None
    try:
        asyncio.run(main_async(args.target, args.duration, Path(args.out_csv), snapshot_dir, args.snapshot_every))
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
