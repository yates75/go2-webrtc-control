"""Small runnable example for safe Go2 control."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from go2_control.client import Go2ControlClient
else:
    from .client import Go2ControlClient


async def run_demo() -> None:
    """Connect, stand up, wag happily, then stop and disconnect."""

    client = Go2ControlClient()
    await client.connect()
    try:
        await client.speed_level(0)
        await client.balance_stand()
        await asyncio.sleep(1.0)
        await client.stand_up()
        await asyncio.sleep(1.0)
        await client.content()
        await asyncio.sleep(1.0)
        await client.walk_for(0.1, duration_s=1.5)
        await client.stop_move()
    finally:
        await client.disconnect()


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
