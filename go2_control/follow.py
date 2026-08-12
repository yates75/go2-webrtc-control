"""Actively follow a detected object by turning/walking toward it.

**This is the first script in this project where the robot moves based on
what a live model thinks it sees, rather than a fixed pre-written
sequence.** Read the safety banner this script prints before running it,
and only run it in a clear, open space with someone ready to Ctrl+C or
physically stop the robot.

Uses the same pretrained YOLO detector as object_tracker.py. A simple
proportional ("P") controller turns the robot toward the object's
horizontal position in frame, and only walks forward when the object is
both roughly centered and not already close (based on its bounding-box
width, as a rough proxy for distance). If the object isn't seen for
--stale-timeout seconds, the robot stops immediately. The whole run is
also capped at --max-seconds regardless of what happens.

All movement still goes through Go2ControlClient.move(), so the same
speed caps as everywhere else in this project apply (0.3 m/s forward,
1.0 rps turn) -- this script also validates its own speed arguments
before connecting, so a bad flag fails immediately instead of mid-run.

Install the extra dependencies once:
    pip install ultralytics opencv-python

Usage:
    python -m go2_control.follow --target person --max-seconds 20
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from go2_control.camera_view import stream_camera
from go2_control.client import MAX_SAFE_WALK_SPEED_MPS, Go2ControlClient
from go2_control.object_tracker import _best_detection, _load_model

TURN_GAIN = 2.0  # proportional gain: turn_rps = -TURN_GAIN * horizontal_error, then clipped
# Sign convention (positive turn_rps = turn left) is taken from cli.py's own
# turn-left/turn-right preset routines, not independently hardware-verified.

Policy = Callable[[float, float, float, float], tuple[float, float]]


@dataclass
class _Target:
    center_x: float
    center_y: float
    box_w: float
    box_h: float
    timestamp: float


def _load_policy(policy_path: Path, forward_cap: float, turn_cap: float) -> Policy:
    """Load a policy trained by train_follow_policy.py as a (forward, turn) callable.

    The model's raw output is always clipped to the same safety caps as
    the hand-coded controller, regardless of what the trained model
    predicts -- a poorly-trained model must never be able to exceed the
    speed limits enforced everywhere else in this project.
    """

    payload = json.loads(policy_path.read_text())
    coefficients = np.array(payload["coefficients"])

    def policy(center_x: float, center_y: float, box_w: float, box_h: float) -> tuple[float, float]:
        features = np.array([center_x, center_y, box_w, box_h, 1.0])
        forward, turn = features @ coefficients
        forward = max(-forward_cap, min(forward_cap, float(forward)))
        turn = max(-turn_cap, min(turn_cap, float(turn)))
        return forward, turn

    return policy


def _print_safety_banner(max_seconds: float, stale_timeout: float) -> None:
    print("=" * 70)
    print("ACTIVE FOLLOWING -- the robot will move on its own based on what")
    print("the camera detects. Clear a wide, open space before continuing.")
    print(f"Stops automatically after {max_seconds:.0f}s, or after")
    print(f"{stale_timeout:.1f}s without seeing the target. Ctrl+C stops it")
    print("immediately at any time.")
    print("=" * 70)


async def follow(
    client: Go2ControlClient,
    target_class: str,
    forward_speed: float,
    max_turn_rps: float,
    center_deadzone: float,
    close_box_width: float,
    detect_interval: float,
    control_interval: float,
    stale_timeout: float,
    max_seconds: float,
    policy: Policy | None = None,
) -> None:
    """Detect `target_class` and drive toward it until it's lost or time runs out.

    Uses the hand-coded proportional controller by default, or `policy`
    (from _load_policy) if one is given -- see --policy in main().
    """

    if forward_speed > MAX_SAFE_WALK_SPEED_MPS:
        raise SystemExit(f"forward_speed must be <= {MAX_SAFE_WALK_SPEED_MPS} m/s")
    if max_turn_rps > 1.0:
        raise SystemExit("max_turn_rps must be <= 1.0")

    _print_safety_banner(max_seconds, stale_timeout)
    print(f"Steering: {'trained policy' if policy else 'hand-coded proportional controller'}")

    model = _load_model()
    latest: _Target | None = None
    last_detect = 0.0

    async def on_frame(frame) -> None:
        nonlocal latest, last_detect
        now = time.monotonic()
        if now - last_detect < detect_interval:
            return
        last_detect = now

        img = frame.to_ndarray(format="bgr24")
        # Inference blocks on CPU for tens-to-hundreds of ms; running it in a
        # thread keeps the event loop free so control_loop's stop-move timing
        # stays responsive instead of stalling for the duration of each detection.
        _, best = await asyncio.to_thread(_best_detection, model, img, target_class)
        if best is not None:
            latest = _Target(
                center_x=best["center_x"],
                center_y=best["center_y"],
                box_w=best["box_w"],
                box_h=best["box_h"],
                timestamp=time.monotonic(),
            )

    await stream_camera(client.conn, on_frame)

    def _hand_coded_action(target: _Target) -> tuple[float, float]:
        error = target.center_x - 0.5
        turn = max(-max_turn_rps, min(max_turn_rps, -TURN_GAIN * error))
        centered = abs(error) < center_deadzone
        forward = forward_speed if (centered and target.box_w < close_box_width) else 0.0
        return forward, turn

    async def control_loop() -> None:
        while True:
            now = time.monotonic()
            if latest is None or (now - latest.timestamp) > stale_timeout:
                await client.stop_move()
            elif policy is not None:
                forward, turn = policy(latest.center_x, latest.center_y, latest.box_w, latest.box_h)
                await client.move(forward, turn_rps=turn)
            else:
                forward, turn = _hand_coded_action(latest)
                await client.move(forward, turn_rps=turn)
            await asyncio.sleep(control_interval)

    try:
        await asyncio.wait_for(control_loop(), timeout=max_seconds)
    except asyncio.TimeoutError:
        print(f"Reached the {max_seconds:.0f}s time limit -- stopping.")
    finally:
        await client.stop_move()


async def main_async(
    target: str,
    forward_speed: float,
    max_turn_rps: float,
    center_deadzone: float,
    close_box_width: float,
    detect_interval: float,
    control_interval: float,
    stale_timeout: float,
    max_seconds: float,
    policy_path: Path | None,
) -> None:
    policy = _load_policy(policy_path, forward_speed, max_turn_rps) if policy_path else None

    client = Go2ControlClient()
    await client.connect()
    try:
        await follow(
            client,
            target,
            forward_speed,
            max_turn_rps,
            center_deadzone,
            close_box_width,
            detect_interval,
            control_interval,
            stale_timeout,
            max_seconds,
            policy=policy,
        )
    finally:
        await client.stop_move()
        await client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Actively follow a detected object with the Go2 camera")
    parser.add_argument("--target", default="person", help="COCO class name to follow")
    parser.add_argument("--forward-speed", type=float, default=0.08, help="Forward speed in m/s, max 0.3")
    parser.add_argument("--max-turn-rps", type=float, default=0.3, help="Max turn rate in rps, max 1.0")
    parser.add_argument("--center-deadzone", type=float, default=0.1, help="How centered (0-0.5) counts as 'aimed at'")
    parser.add_argument("--close-box-width", type=float, default=0.5, help="Box width fraction above which the object is 'close'")
    parser.add_argument("--detect-interval", type=float, default=0.3, help="Minimum seconds between detection passes")
    parser.add_argument("--control-interval", type=float, default=0.1, help="Seconds between movement commands")
    parser.add_argument("--stale-timeout", type=float, default=1.0, help="Seconds without a detection before stopping")
    parser.add_argument("--max-seconds", type=float, default=30.0, help="Hard time limit for the whole run")
    parser.add_argument(
        "--policy",
        default=None,
        help="Path to a policy trained with train_follow_policy.py; omit to use the hand-coded controller",
    )
    args = parser.parse_args()

    try:
        asyncio.run(
            main_async(
                args.target,
                args.forward_speed,
                args.max_turn_rps,
                args.center_deadzone,
                args.close_box_width,
                args.detect_interval,
                args.control_interval,
                args.stale_timeout,
                args.max_seconds,
                Path(args.policy) if args.policy else None,
            )
        )
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
