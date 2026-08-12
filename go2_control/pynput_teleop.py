"""Global keyboard teleop for the Unitree Go2 Pro using pynput."""

from __future__ import annotations

import asyncio
import sys
import threading
import time
from dataclasses import dataclass, field

from pynput import keyboard

from .client import Go2ControlClient


FORWARD_SPEED_MPS = 0.3  # Keep forward/back speed at or below the shell-safe limit.
TURN_RATE_RPS = 0.3  # Use a conservative in-place turn rate.
CONTROL_INTERVAL_S = 0.1  # Send motion updates often enough for smooth movement.


DEADMAN_TIMEOUT_S = 0.25  # Stop the robot if no motion key is held for this long.

ACTION_LABELS: dict[str, str] = {
    "forward":  "▲  forward",
    "backward": "▼  backward",
    "left":     "◀  turn left",
    "right":    "▶  turn right",
    "stop":     "■  stopped",
}


@dataclass
class TeleopState:
    """Shared state between the pynput thread and the asyncio control loop."""

    action: str = "stop"
    quit_requested: bool = False
    last_motion_time: float = field(default_factory=time.monotonic)  # Timestamp of the last motion key press.
    lock: threading.Lock = field(default_factory=threading.Lock)


def set_action(state: TeleopState, action: str) -> None:
    """Update the current desired action in a thread-safe way."""

    with state.lock:
        state.action = action
        if action not in {"stop", "quit"}:  # Record when a motion key was last held.
            state.last_motion_time = time.monotonic()


def request_quit(state: TeleopState) -> None:
    """Ask the control loop to sit the robot down and exit."""

    with state.lock:
        state.action = "stop"
        state.quit_requested = True


def get_state_snapshot(state: TeleopState) -> tuple[str, bool, float]:
    """Read the current action, quit flag, and last motion timestamp atomically."""

    with state.lock:
        return state.action, state.quit_requested, state.last_motion_time


def print_status(action: str) -> None:
    """Overwrite the current terminal line with the live action label."""

    label = ACTION_LABELS.get(action, action)
    sys.stdout.write(f"\rAction: {label:<20}")  # \r returns to line start so the line overwrites itself.
    sys.stdout.flush()


def key_to_action(key) -> str | None:
    """Map a pynput key to a robot action name."""

    if key == keyboard.Key.space:
        return "stop"

    if isinstance(key, keyboard.KeyCode) and key.char:
        char = key.char.lower()
        if char == "w":
            return "forward"
        if char == "s":
            return "backward"
        if char == "a":
            return "left"
        if char == "d":
            return "right"
        if char == "q":
            return "quit"

    return None


def build_listener(state: TeleopState) -> keyboard.Listener:
    """Create the global keyboard listener."""

    def on_press(key):
        action = key_to_action(key)
        if action == "quit":
            request_quit(state)
        elif action is not None:
            set_action(state, action)

    def on_release(key):
        action = key_to_action(key)
        if action in {"forward", "backward", "left", "right"}:
            set_action(state, "stop")

    return keyboard.Listener(on_press=on_press, on_release=on_release)


async def control_loop(client: Go2ControlClient, state: TeleopState) -> None:
    """Keep sending the current motion command until Q is pressed."""

    last_action = "stop"
    while True:
        action, quit_requested, last_motion_time = get_state_snapshot(state)

        if quit_requested:
            print_status("stop")
            print()  # Move to a new line before the exit message.
            print("Sitting down and quitting...")
            await client.stop_move()
            await asyncio.sleep(0.2)
            await client.sit()
            await asyncio.sleep(1.5)
            return

        # Deadman check: if the action is a motion but no key has been pressed
        # recently, treat it as a stop. This guards against a missed key-release
        # event that would otherwise leave the robot walking indefinitely.
        if action not in {"stop"} and time.monotonic() - last_motion_time > DEADMAN_TIMEOUT_S:
            action = "stop"
            set_action(state, "stop")

        if action == "forward":
            await client.move(FORWARD_SPEED_MPS)
        elif action == "backward":
            await client.move(-FORWARD_SPEED_MPS)
        elif action == "left":
            await client.move(0.0, turn_rps=TURN_RATE_RPS)
        elif action == "right":
            await client.move(0.0, turn_rps=-TURN_RATE_RPS)
        else:
            if last_action != "stop":
                await client.stop_move()

        if action != last_action:  # Only reprint when something changes to avoid flicker.
            print_status(action)

        last_action = action
        await asyncio.sleep(CONTROL_INTERVAL_S)


async def main_async() -> None:
    """Connect, stand the robot up, and start the global key teleop loop."""

    client = Go2ControlClient()
    state = TeleopState()
    listener = build_listener(state)

    await client.connect()
    try:
        await client.stand_up()
        await asyncio.sleep(2.0)

        listener.start()
        print("Go2 teleop active. Hold a key to move; release to stop (deadman).")
        print("  W forward  S backward  A left  D right  Space stop  Q sit+quit")
        print_status("stop")
        await control_loop(client, state)
    finally:
        listener.stop()
        await client.disconnect()


def main() -> None:
    """Entry point for the console script."""

    asyncio.run(main_async())


if __name__ == "__main__":
    main()
