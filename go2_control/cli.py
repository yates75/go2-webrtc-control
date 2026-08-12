"""Command-line interface for safe Go2 control."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass

from .client import Go2ControlClient
from .config import load_config

try:
    from go2_webrtc_driver.go2_webrtc_connection import WebRTCConnectionMethod
except ModuleNotFoundError:
    from go2_webrtc_driver.webrtc_driver import WebRTCConnectionMethod


@dataclass(frozen=True, slots=True)
class MenuItem:
    number: str
    label: str
    action: str


MENU_ITEMS = [
    MenuItem("1", "balance-stand", "balance-stand"),
    MenuItem("2", "stand-up", "stand-up"),
    MenuItem("3", "stand-down", "stand-down"),
    MenuItem("4", "sit", "sit"),
    MenuItem("5", "stop", "stop"),
    MenuItem("6", "hello", "hello"),
    MenuItem("7", "content", "content"),
    MenuItem("8", "heart-pose", "heart-pose"),
    MenuItem("9", "stretch", "stretch"),
    MenuItem("10", "walk", "walk"),
    MenuItem("11", "walk-for", "walk-for"),
    MenuItem("12", "routine: greet", "routine:greet"),
    MenuItem("13", "routine: calm-start", "routine:calm-start"),
    MenuItem("14", "routine: short-walk", "routine:short-walk"),
    MenuItem("15", "routine: reset", "routine:reset"),
    MenuItem("16", "routine: turn-left", "routine:turn-left"),
    MenuItem("17", "routine: turn-right", "routine:turn-right"),
    MenuItem("18", "routine: back-up-slowly", "routine:back-up-slowly"),
]


def build_parser() -> argparse.ArgumentParser:
    """Build the small CLI used for ad-hoc control."""

    parser = argparse.ArgumentParser(description="Safe async control for a Unitree Go2 Pro")
    parser.add_argument("--config", default=None, help="Path to a TOML config file")
    parser.add_argument(
        "--connection-mode",
        choices=["ap", "sta", "remote"],
        default="ap",
        help="Connection mode: ap (LocalAP), sta (LocalSTA), or remote",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("balance-stand", help="Stand up and balance")
    subparsers.add_parser("stand-up", help="Stand up")
    subparsers.add_parser("stand-down", help="Stand down")
    subparsers.add_parser("sit", help="Sit down")
    subparsers.add_parser("stop", help="Stop motion")
    subparsers.add_parser("hello", help="Wave hello")
    subparsers.add_parser("content", help="Happy wagging")
    subparsers.add_parser("heart-pose", help="Heart pose")
    subparsers.add_parser("stretch", help="Stretch")

    routine = subparsers.add_parser("routine", help="Run a named safe preset routine")
    routine.add_argument(
        "name",
        choices=[
            "greet",
            "calm-start",
            "short-walk",
            "reset",
            "turn-left",
            "turn-right",
            "back-up-slowly",
        ],
        help="Routine name",
    )

    walk = subparsers.add_parser("walk", help="Walk at a capped speed")
    walk.add_argument("--forward", type=float, default=0.1, help="Forward speed in m/s, max 0.3")
    walk.add_argument("--sideways", type=float, default=0.0, help="Sideways speed in m/s, max 0.3")
    walk.add_argument("--turn", type=float, default=0.0, help="Turn rate in rps")

    timed_walk = subparsers.add_parser("walk-for", help="Walk for a limited time and stop automatically")
    timed_walk.add_argument("--forward", type=float, default=0.1, help="Forward speed in m/s, max 0.3")
    timed_walk.add_argument("--sideways", type=float, default=0.0, help="Sideways speed in m/s, max 0.3")
    timed_walk.add_argument("--turn", type=float, default=0.0, help="Turn rate in rps")
    timed_walk.add_argument("--duration", type=float, default=2.0, help="Duration in seconds")
    timed_walk.add_argument("--interval", type=float, default=0.1, help="Command interval in seconds")

    subparsers.add_parser("menu", help="Open a tiny interactive command menu")

    return parser


def print_menu() -> None:
    """Show a compact interactive menu."""

    print("\nGo2 control menu")
    for item in MENU_ITEMS:
        print(f"{item.number}) {item.label}")
    print("0) quit")


def prompt_float(prompt: str, default: float) -> float:
    """Read a float from the terminal with a default value."""

    raw_value = input(f"{prompt} [{default}]: ").strip()
    if not raw_value:
        return default
    return float(raw_value)


async def run_routine(client: Go2ControlClient, name: str) -> None:
    """Run one named safe preset routine."""

    if name == "greet":
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.hello()
        await asyncio.sleep(1.0)
        await client.content()
        await asyncio.sleep(1.0)
        await client.stop_move()
    elif name == "calm-start":
        await client.speed_level(0)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(2.0)
        await client.stop_move()
    elif name == "short-walk":
        await client.speed_level(0)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(2.0)
        await client.walk_for_default(duration_s=2.0, interval_s=0.1)
    elif name == "reset":
        await client.stop_move()
        await asyncio.sleep(0.5)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stop_move()
    elif name == "turn-left":
        await client.speed_level(0)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(2.0)
        await client.walk_for(0.0, duration_s=1.5, turn_rps=0.2, interval_s=0.1)
    elif name == "turn-right":
        await client.speed_level(0)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(2.0)
        await client.walk_for(0.0, duration_s=1.5, turn_rps=-0.2, interval_s=0.1)
    elif name == "back-up-slowly":
        await client.speed_level(0)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(2.0)
        await client.walk_for(-0.08, duration_s=2.0, interval_s=0.1)
    else:
        raise ValueError(f"Unknown routine: {name}")


async def run_menu(client: Go2ControlClient) -> None:
    """Run a tiny interactive command loop."""

    menu_actions = {item.number: item.action for item in MENU_ITEMS}

    while True:
        print_menu()
        choice = input("Select a command: ").strip()

        if choice == "0":
            return
        action = menu_actions.get(choice)
        if action == "balance-stand":
            await client.balance_stand()
        elif action == "stand-up":
            await client.stand_up()
        elif action == "stand-down":
            await client.stand_down()
        elif action == "sit":
            await client.sit()
        elif action == "stop":
            await client.stop_move()
        elif action == "hello":
            await client.hello()
        elif action == "content":
            await client.content()
        elif action == "heart-pose":
            await client.heart_pose()
        elif action == "stretch":
            await client.stretch()
        elif action == "walk":
            forward = prompt_float("Forward speed m/s", client.config.default_walk_speed_mps)
            sideways = prompt_float("Sideways speed m/s", 0.0)
            turn = prompt_float("Turn rate rps", 0.0)
            await client.move(forward, sideways_mps=sideways, turn_rps=turn)
        elif action == "walk-for":
            duration = prompt_float("Walk duration seconds", 2.0)
            sideways = prompt_float("Sideways speed m/s", 0.0)
            turn = prompt_float("Turn rate rps", 0.0)
            interval = prompt_float("Command interval seconds", 0.1)
            await client.walk_for_default(duration, sideways_mps=sideways, turn_rps=turn, interval_s=interval)
        elif action and action.startswith("routine:"):
            await run_routine(client, action.split(":", 1)[1])
        else:
            print("Unknown choice. Try again.")


async def run_command(args: argparse.Namespace) -> None:
    """Connect, run the selected command, and disconnect."""

    config = load_config(args.config) if getattr(args, "config", None) else load_config()
    mode_lookup = {
        "ap": WebRTCConnectionMethod.LocalAP,
        "sta": WebRTCConnectionMethod.LocalSTA,
        "remote": WebRTCConnectionMethod.Remote,
    }
    client = Go2ControlClient(mode_lookup[args.connection_mode])
    client.set_config(config)
    await client.connect()
    try:
        print(
            f"Connected to Go2 config: WiFi={client.config.wifi_name}, "
            f"IP={client.config.robot_ip}, default speed={client.config.default_walk_speed_mps} m/s"
        )
        if args.command == "balance-stand":
            await client.balance_stand()
        elif args.command == "stand-up":
            await client.stand_up()
        elif args.command == "stand-down":
            await client.stand_down()
        elif args.command == "sit":
            await client.sit()
        elif args.command == "stop":
            await client.stop_move()
        elif args.command == "hello":
            await client.hello()
        elif args.command == "content":
            await client.content()
        elif args.command == "heart-pose":
            await client.heart_pose()
        elif args.command == "stretch":
            await client.stretch()
        elif args.command == "walk":
            await client.stand_up()
            await asyncio.sleep(2.0)
            await client.move(args.forward, sideways_mps=args.sideways, turn_rps=args.turn)
        elif args.command == "walk-for":
            await client.stand_up()
            await asyncio.sleep(2.0)
            await client.walk_for(
                args.forward,
                args.duration,
                sideways_mps=args.sideways,
                turn_rps=args.turn,
                interval_s=args.interval,
            )
        elif args.command == "menu":
            await run_menu(client)
        elif args.command == "routine":
            await run_routine(client, args.name)
    finally:
        await client.disconnect()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run_command(args))


if __name__ == "__main__":
    main()
