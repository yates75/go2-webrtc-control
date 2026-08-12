"""Detect and log a moving object's position using the Go2's LIDAR feed.

Passive only -- this never sends a movement command, it only watches and
records. Uses a simple, fully-explainable algorithm rather than a heavy
clustering library (no new dependency beyond numpy, already installed):

1. **Calibrate**: for the first `--calibrate-frames` messages, assume the
   space is empty and record every voxel (a coarse 3D grid cell) the
   LIDAR reports as "background". Run calibration with a clear space, per
   the safety note at the top of the tutorial.
2. **Track**: for every message after that, any voxel *not* seen during
   calibration is "new" -- most likely the object that has since entered
   the space (or moved within it). New voxels are grouped into clusters
   (voxels touching each other, 6-connected), and the centroid of the
   largest cluster is logged as the tracked object's position.

This is a coarse, classroom-appropriate approach, not a research-grade
tracker -- it will also flag a person walking behind the robot, furniture
being moved, etc. as "the object."

Honesty note: the decoded LIDAR payload's exact field names have not been
confirmed against real hardware (see lidar_view.py's caveat, Part 3 of the
tutorial). `_extract_points()` tries several common field names/shapes
defensively; if none match, it prints the raw payload's keys once so you
can see the real structure and adjust the extraction logic to match.

Usage:
    python -m go2_control.lidar_tracker --calibrate-frames 10 --count 30
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import time
from pathlib import Path

import numpy as np

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
from go2_webrtc_driver.constants import RTC_TOPIC

VoxelSet = set[tuple[int, int, int]]

_NEIGHBOR_OFFSETS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def _extract_points(payload) -> np.ndarray | None:
    """Best-effort extraction of an (N, 3) point array from a decoded LIDAR message."""

    candidates = payload
    if isinstance(payload, dict):
        candidates = None
        for key in ("positions", "points", "point_cloud", "xyz", "data"):
            if key in payload:
                candidates = payload[key]
                break
        if candidates is None:
            return None

    try:
        arr = np.asarray(candidates, dtype=float)
    except (TypeError, ValueError):
        return None

    if arr.ndim == 1:
        if arr.size == 0 or arr.size % 3 != 0:
            return None
        arr = arr.reshape(-1, 3)
    if arr.ndim != 2 or arr.shape[1] < 3:
        return None
    return arr[:, :3]


def _voxelize(points: np.ndarray, voxel_size: float) -> VoxelSet:
    idx = np.floor(points / voxel_size).astype(int)
    return {tuple(row) for row in idx}


def _largest_cluster(voxels: VoxelSet) -> VoxelSet | None:
    """Connected-component clustering (6-connectivity) over occupied voxels."""

    remaining = set(voxels)
    best: VoxelSet | None = None

    while remaining:
        seed = remaining.pop()
        stack = [seed]
        cluster = {seed}
        while stack:
            v = stack.pop()
            for dx, dy, dz in _NEIGHBOR_OFFSETS:
                neighbor = (v[0] + dx, v[1] + dy, v[2] + dz)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    cluster.add(neighbor)
                    stack.append(neighbor)
        if best is None or len(cluster) > len(best):
            best = cluster

    return best


async def track_object(
    conn: Go2WebRTCConnection,
    calibrate_frames: int,
    count: int,
    voxel_size: float,
    min_cluster_voxels: int,
    out_csv: Path,
) -> None:
    """Calibrate a background voxel set, then log `count` tracked-object positions."""

    out_csv.parent.mkdir(parents=True, exist_ok=True)

    background: VoxelSet = set()
    calibrated = 0
    logged = 0
    warned_bad_payload = False
    done = asyncio.Event()

    with out_csv.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "found", "centroid_x", "centroid_y", "centroid_z", "cluster_voxels"])

        def on_message(message: dict) -> None:
            nonlocal calibrated, logged, warned_bad_payload

            data = message.get("data", {})
            payload = data.get("data") if isinstance(data, dict) and isinstance(data.get("data"), dict) else data
            points = _extract_points(payload)

            if points is None or len(points) == 0:
                if not warned_bad_payload:
                    keys = list(payload.keys()) if isinstance(payload, dict) else type(payload)
                    print(f"Could not find point data in LIDAR message (payload: {keys}). Skipping.")
                    warned_bad_payload = True
                return

            frame_voxels = _voxelize(points, voxel_size)

            if calibrated < calibrate_frames:
                background.update(frame_voxels)
                calibrated += 1
                print(f"Calibrating background ({calibrated}/{calibrate_frames}), {len(background)} voxels so far")
                if calibrated == calibrate_frames:
                    print("Calibration complete. Tracking new objects now.")
                return

            foreground = frame_voxels - background
            cluster = _largest_cluster(foreground) if foreground else None
            timestamp = time.time()

            if cluster and len(cluster) >= min_cluster_voxels:
                centers = np.array(list(cluster), dtype=float) * voxel_size + (voxel_size / 2)
                centroid = centers.mean(axis=0)
                writer.writerow([timestamp, True, centroid[0], centroid[1], centroid[2], len(cluster)])
                print(f"[{logged}] object at x={centroid[0]:.2f} y={centroid[1]:.2f} z={centroid[2]:.2f} ({len(cluster)} voxels)")
            else:
                writer.writerow([timestamp, False, "", "", "", 0])
                print(f"[{logged}] no object above {min_cluster_voxels}-voxel threshold")

            handle.flush()
            logged += 1
            if logged >= count:
                done.set()

        await conn.datachannel.disableTrafficSaving(True)
        conn.datachannel.pub_sub.subscribe(RTC_TOPIC["ULIDAR_ARRAY"], on_message)
        conn.datachannel.pub_sub.publish_without_callback(RTC_TOPIC["ULIDAR_SWITCH"], "on")

        try:
            await done.wait()
        finally:
            conn.datachannel.pub_sub.unsubscribe(RTC_TOPIC["ULIDAR_ARRAY"])
            conn.datachannel.pub_sub.publish_without_callback(RTC_TOPIC["ULIDAR_SWITCH"], "off")

    print(f"Logged {logged} tracked positions to {out_csv}")


async def main_async(calibrate_frames: int, count: int, voxel_size: float, min_cluster_voxels: int, out_csv: Path) -> None:
    conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    await conn.connect()
    try:
        await track_object(conn, calibrate_frames, count, voxel_size, min_cluster_voxels, out_csv)
    finally:
        await conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect and log a moving object's position using the Go2 LIDAR feed")
    parser.add_argument("--calibrate-frames", type=int, default=10, help="Messages used to learn the empty-space background")
    parser.add_argument("--count", type=int, default=30, help="Number of tracked positions to log after calibration")
    parser.add_argument("--voxel-size", type=float, default=0.1, help="Grid cell size in meters")
    parser.add_argument("--min-cluster-voxels", type=int, default=3, help="Minimum cluster size to count as a real object")
    parser.add_argument("--out-csv", default="lidar_track.csv", help="CSV output path")
    args = parser.parse_args()
    asyncio.run(main_async(args.calibrate_frames, args.count, args.voxel_size, args.min_cluster_voxels, Path(args.out_csv)))


if __name__ == "__main__":
    main()
