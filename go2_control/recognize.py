"""Run a classifier you trained yourself (train_classifier.py) live against the camera feed.

Passive only -- this never sends a movement command. Prints the model's
top prediction and confidence for each processed frame, and logs the
same to a CSV.

Usage:
    python -m go2_control.recognize --model trained_classifier.pt --count 20
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


def _load_trained_model(model_path: Path):
    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise SystemExit("Recognition needs the 'ultralytics' package: pip install ultralytics") from exc

    if not model_path.exists():
        raise SystemExit(f"Model file not found: {model_path}. Train one first with train_classifier.py.")
    return YOLO(str(model_path))


async def recognize_live(
    conn: Go2WebRTCConnection, model_path: Path, count: int, interval_s: float, out_csv: Path
) -> None:
    model = _load_trained_model(model_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    logged = 0
    last_processed = 0.0
    done = asyncio.Event()

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "predicted_label", "confidence"])

        async def on_frame(frame) -> None:
            nonlocal logged, last_processed
            now = time.monotonic()
            if now - last_processed < interval_s:
                return
            last_processed = now

            img = frame.to_ndarray(format="bgr24")
            results = await asyncio.to_thread(lambda: model(img, verbose=False)[0])
            label = results.names[int(results.probs.top1)]
            confidence = float(results.probs.top1conf)

            writer.writerow([time.time(), label, confidence])
            print(f"[{logged}] {label} (confidence={confidence:.2f})")
            handle.flush()

            logged += 1
            if logged >= count:
                done.set()

        await stream_camera(conn, on_frame)
        await done.wait()

    print(f"Logged {logged} predictions to {out_csv}")


async def main_async(model_path: Path, count: int, interval: float, out_csv: Path) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await recognize_live(conn, model_path, count, interval, out_csv)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a self-trained classifier live against the Go2 camera")
    parser.add_argument("--model", default="trained_classifier.pt", help="Path to a model trained with train_classifier.py")
    parser.add_argument("--count", type=int, default=20, help="Number of predictions to log")
    parser.add_argument("--interval", type=float, default=0.5, help="Minimum seconds between processed frames")
    parser.add_argument("--out-csv", default="recognize_log.csv", help="CSV output path")
    args = parser.parse_args()
    asyncio.run(main_async(Path(args.model), args.count, args.interval, Path(args.out_csv)))


if __name__ == "__main__":
    main()
