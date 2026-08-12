"""Detect and track objects' positions from the Go2's camera feed over time.

Passive only -- this never sends a movement command, it only watches and
records. Uses a small pretrained YOLO model (Ultralytics) with its
built-in persistent tracker to detect everyday objects (COCO classes:
"person", "sports ball", "bottle", "cell phone", ...) and follow each one
with a stable ID across frames, so multiple simultaneous people/objects
can be told apart -- not just "something of this class is in frame."

First run downloads the model weights (~6MB) from the internet -- if
you're on a restricted school network, run this once somewhere with
internet access first so the weights get cached locally.

Install the extra dependencies once:
    pip install ultralytics opencv-python

Usage:
    python -m go2_control.object_tracker --target person --count 30 --interval 0.5
    python -m go2_control.object_tracker --target "sports ball" --save-annotated
    python -m go2_control.object_tracker --live --target person
    python -m go2_control.object_tracker --live --all-classes
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


def _load_model():
    """Lazily import and load the pretrained YOLO model (avoids a hard torch dependency)."""

    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise SystemExit("Object tracking needs the 'ultralytics' package: pip install ultralytics") from exc

    return YOLO("yolov8n.pt")


def _tracked_detections(model, img, target_class: str | None):
    """Run YOLO's persistent tracker on one frame; return (results, matches).

    `matches` is a list of dicts (one per tracked box that matches
    `target_class`, or every box if `target_class` is None), each with
    track_id/class_name/confidence/center_x/center_y/box_w/box_h (position
    fields normalized to [0, 1]). `results` is the raw Ultralytics result
    (used for `.plot()` when saving annotated frames).

    Uses `.track(persist=True)` rather than plain detection so each object
    keeps the same `track_id` across frames instead of getting a fresh,
    unrelated detection every time -- this is what makes it possible to
    tell multiple people/objects apart over time instead of just knowing
    "something of this class is somewhere in frame."
    """

    results = model.track(img, persist=True, verbose=False)[0]
    height, width = img.shape[:2]
    matches = []
    for box in results.boxes:
        class_name = model.names[int(box.cls[0])]
        if target_class is not None and class_name != target_class:
            continue
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        matches.append(
            {
                "track_id": int(box.id[0]) if box.id is not None else -1,
                "class_name": class_name,
                "confidence": float(box.conf[0]),
                "center_x": ((x1 + x2) / 2) / width,
                "center_y": ((y1 + y2) / 2) / height,
                "box_w": (x2 - x1) / width,
                "box_h": (y2 - y1) / height,
            }
        )
    return results, matches


async def track_object(
    conn: Go2WebRTCConnection,
    target_class: str | None,
    count: int,
    interval_s: float,
    out_csv: Path,
    annotated_dir: Path | None = None,
) -> None:
    """Track `target_class` (or every class, if None) in the camera feed for `count` frames.

    Every tracked object gets its own persistent `track_id` (stable across
    frames via YOLO's built-in tracker) plus a position, so multiple
    simultaneous people/objects can be told apart in the resulting CSV --
    one row per tracked object per frame, not just one row per frame.
    Frames where nothing was found still get a single found=False row so
    gaps are visible.
    """

    model = _load_model()
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if annotated_dir is not None:
        annotated_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    done = asyncio.Event()
    last_processed = 0.0

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["timestamp", "frame", "found", "track_id", "class_name", "confidence", "center_x", "center_y", "box_w", "box_h"]
        )

        async def on_frame(frame) -> None:
            nonlocal processed, last_processed
            now = time.monotonic()
            if now - last_processed < interval_s:
                return
            last_processed = now

            img = frame.to_ndarray(format="bgr24")
            results, matches = await asyncio.to_thread(_tracked_detections, model, img, target_class)

            timestamp = time.time()
            if matches:
                for match in matches:
                    writer.writerow(
                        [
                            timestamp,
                            processed,
                            True,
                            match["track_id"],
                            match["class_name"],
                            match["confidence"],
                            match["center_x"],
                            match["center_y"],
                            match["box_w"],
                            match["box_h"],
                        ]
                    )
                    print(
                        f"[{processed}] {match['class_name']} id={match['track_id']} at "
                        f"({match['center_x']:.2f}, {match['center_y']:.2f}) confidence={match['confidence']:.2f}"
                    )
            else:
                writer.writerow([timestamp, processed, False, "", "", "", "", "", "", ""])
                print(f"[{processed}] nothing tracked")

            if annotated_dir is not None:
                import cv2

                annotated = results.plot()
                cv2.imwrite(str(annotated_dir / f"frame_{processed:04d}.jpg"), annotated)

            handle.flush()
            processed += 1
            if processed >= count:
                done.set()

        await stream_camera(conn, on_frame)
        await done.wait()

    print(f"Processed {processed} frames, logged to {out_csv}")


async def live_track(conn: Go2WebRTCConnection, target_class: str | None) -> None:
    """Show a live cv2 window with detections: box, class, persistent track ID,
    normalized position, and confidence drawn on each match.

    Uses YOLO's built-in `.track()` (not plain detection) so each object gets
    a persistent ID that stays the same across frames as long as it's
    trackable, instead of just a fresh per-frame detection. Press 'q' to quit.
    """

    import cv2

    model = _load_model()
    done = asyncio.Event()

    async def on_frame(frame) -> None:
        img = frame.to_ndarray(format="bgr24")
        height, width = img.shape[:2]
        results = await asyncio.to_thread(model.track, img, persist=True, verbose=False)
        result = results[0]

        for box in result.boxes:
            class_name = model.names[int(box.cls[0])]
            if target_class is not None and class_name != target_class:
                continue

            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            track_id = int(box.id[0]) if box.id is not None else -1
            center_x = ((x1 + x2) / 2) / width
            center_y = ((y1 + y2) / 2) / height

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_name} id={track_id} ({center_x:.2f},{center_y:.2f}) {confidence:.2f}"
            cv2.putText(
                img, label, (x1, max(y1 - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

        cv2.imshow("Go2 object tracker", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            done.set()

    try:
        await stream_camera(conn, on_frame)
        await done.wait()
    finally:
        cv2.destroyAllWindows()


async def main_async(
    target: str | None,
    count: int,
    interval: float,
    out_csv: Path,
    annotated_dir: Path | None,
    live: bool,
) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        if live:
            await live_track(conn, target)
        else:
            await track_object(conn, target, count, interval, out_csv, annotated_dir)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect and log a moving object's position from the Go2 camera")
    parser.add_argument("--target", default="person", help="COCO class name to track, e.g. person, sports ball, bottle")
    parser.add_argument("--count", type=int, default=30, help="Number of detection samples to log")
    parser.add_argument("--interval", type=float, default=0.5, help="Minimum seconds between processed frames")
    parser.add_argument("--out-csv", default="object_track.csv", help="CSV output path")
    parser.add_argument("--save-annotated", action="store_true", help="Save annotated JPEGs with detection boxes drawn")
    parser.add_argument("--annotated-dir", default="object_track_frames", help="Directory for annotated snapshots")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Show a live cv2 window with box/ID/position overlaid instead of logging to CSV",
    )
    parser.add_argument(
        "--all-classes",
        action="store_true",
        help="Track/show every detected class instead of filtering to --target",
    )
    args = parser.parse_args()

    annotated_dir = Path(args.annotated_dir) if args.save_annotated else None
    effective_target = None if args.all_classes else args.target
    asyncio.run(
        main_async(effective_target, args.count, args.interval, Path(args.out_csv), annotated_dir, args.live)
    )


if __name__ == "__main__":
    main()
