"""Capture a labeled image dataset from the Go2 camera for classifier training.

Hold the object (or aim at the scene) you want to teach the robot to
recognize, then run this once per class label. Images are saved directly
into the folder structure Ultralytics classification training expects:

    <dataset-dir>/train/<label>/img_0000.jpg
    <dataset-dir>/val/<label>/img_0000.jpg

Run it multiple times with different --label values to build up a
multi-class dataset, then train with train_classifier.py.

Usage:
    python -m go2_control.dataset_capture --label ball --count 40 --interval 0.3
    python -m go2_control.dataset_capture --label shoe --count 40 --interval 0.3
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

from go2_control.camera_view import stream_camera


async def capture_labeled_images(
    conn: Go2WebRTCConnection,
    label: str,
    dataset_dir: Path,
    count: int,
    interval_s: float,
    val_fraction: float,
) -> None:
    """Save `count` images for `label`, splitting into train/val by `val_fraction`."""

    train_dir = dataset_dir / "train" / label
    val_dir = dataset_dir / "val" / label
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    val_every = max(1, round(1 / val_fraction)) if val_fraction > 0 else 0
    saved = 0
    done = asyncio.Event()

    async def on_frame(frame) -> None:
        nonlocal saved
        if saved >= count:
            return

        is_val = val_every > 0 and (saved + 1) % val_every == 0
        out_dir = val_dir if is_val else train_dir
        image_path = out_dir / f"img_{saved:04d}.jpg"
        frame.to_image().save(image_path)
        print(f"Saved {image_path} ({'val' if is_val else 'train'})")

        saved += 1
        if saved >= count:
            done.set()
        else:
            await asyncio.sleep(interval_s)

    await stream_camera(conn, on_frame)
    await done.wait()
    print(f"Captured {saved} images for label '{label}' in {dataset_dir}")


async def main_async(label: str, dataset_dir: Path, count: int, interval: float, val_fraction: float) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await capture_labeled_images(conn, label, dataset_dir, count, interval, val_fraction)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture a labeled image set from the Go2 camera for training")
    parser.add_argument("--label", required=True, help="Class name for these images, e.g. 'ball'")
    parser.add_argument("--dataset-dir", default="dataset", help="Root dataset folder (shared across labels)")
    parser.add_argument("--count", type=int, default=40, help="Number of images to capture")
    parser.add_argument("--interval", type=float, default=0.3, help="Seconds between captures")
    parser.add_argument("--val-fraction", type=float, default=0.2, help="Fraction of images set aside for validation")
    args = parser.parse_args()
    asyncio.run(main_async(args.label, Path(args.dataset_dir), args.count, args.interval, args.val_fraction))


if __name__ == "__main__":
    main()
