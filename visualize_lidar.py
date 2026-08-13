"""Visualize a recorded LIDAR frame (from `go2_control.lidar_view --record`).

The `positions` array in each frame is a flat list of (x, y, z) voxel-grid
indices (uint8, not meters -- see STUDENT_TUTORIAL.md Part 3), so this
scales by --voxel-size to get real-world-ish coordinates before plotting.

Usage:
    python visualize_lidar.py lidar_recording/frame_0000.pkl
    python visualize_lidar.py lidar_recording/frame_0000.pkl --2d
    python visualize_lidar.py lidar_recording/frame_0000.pkl --out frame.png
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_points(pkl_path: Path, voxel_size: float) -> np.ndarray:
    with pkl_path.open("rb") as handle:
        frame = pickle.load(handle)
    positions = frame["positions"].reshape(-1, 3).astype(float)
    return positions * voxel_size


def plot_3d(points: np.ndarray, title: str):
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=1, c=points[:, 2], cmap="viridis")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title(title)
    fig.colorbar(scatter, ax=ax, shrink=0.6, label="height (m)")
    return fig


def plot_2d(points: np.ndarray, title: str):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(points[:, 0], points[:, 1], s=1)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title(title)
    ax.set_aspect("equal")
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize a recorded LIDAR frame")
    parser.add_argument("pkl_path", type=Path, help="Path to a frame_XXXX.pkl file")
    parser.add_argument("--voxel-size", type=float, default=0.1, help="Meters per voxel grid unit")
    parser.add_argument("--2d", dest="two_d", action="store_true", help="Top-down 2D view instead of 3D")
    parser.add_argument("--out", type=Path, default=None, help="Save to a PNG instead of opening a window")
    args = parser.parse_args()

    points = load_points(args.pkl_path, args.voxel_size)
    print(f"Loaded {points.shape[0]} points from {args.pkl_path}")
    print(f"Extent: x=[{points[:,0].min():.2f}, {points[:,0].max():.2f}]  "
          f"y=[{points[:,1].min():.2f}, {points[:,1].max():.2f}]  "
          f"z=[{points[:,2].min():.2f}, {points[:,2].max():.2f}]  (meters)")

    title = f"{args.pkl_path.name} -- {points.shape[0]} points"
    fig = plot_2d(points, title) if args.two_d else plot_3d(points, title)

    if args.out:
        fig.savefig(args.out, dpi=150)
        print(f"Saved to {args.out}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
