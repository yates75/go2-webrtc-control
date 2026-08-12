"""Go2 Pro repeat routine: tilt one way, then the other, then sit down."""

import asyncio  # Run the async control flow.
import math  # Convert degrees to radians for tilt commands.

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    # Newer go2-webrtc-connect exposes these from webrtc_driver.
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod


ROBOT_CONNECTION_METHOD = WebRTCConnectionMethod.LocalAP  # Connect through the Go2's own WiFi hotspot.
COMMAND_TOPIC = "rt/api/sport/request"  # Topic used by the sport API.
COMMAND_ID = 1  # Simple message identity for this script.

NUM_REPEATS = 3  # Change this to control how many times the loop runs.
TURN_SIDE = "right"  # Change this to "left" or "right" to choose the first tilt direction.
TILT_ANGLE_DEGREES = 12.0  # Small, gentle body tilt for each side.
COUNTDOWN_SECONDS = 3  # Safety pause before the first motion.
PAUSE_BETWEEN_TILTS_SECONDS = 1.0  # Pause briefly between the two tilts.
PAUSE_BETWEEN_LOOPS_SECONDS = 1.0  # Pause briefly between full loop repeats.

ROUTINE_STEPS = [  # Define the repeated movement pattern as a list of step dictionaries.
    {"action": "tilt", "params": {"side": TURN_SIDE, "degrees": TILT_ANGLE_DEGREES}, "pause": PAUSE_BETWEEN_TILTS_SECONDS},  # Tilt toward the chosen side.
    {"action": "tilt", "params": {"side": "left" if TURN_SIDE == "right" else "right", "degrees": TILT_ANGLE_DEGREES}, "pause": PAUSE_BETWEEN_TILTS_SECONDS},  # Tilt back the other way.
]


async def maybe_await(value):  # Await coroutine results and pass through regular values.
    if asyncio.iscoroutine(value):  # Check whether the returned value is awaitable.
        return await value  # Await async methods when needed.
    return value  # Return plain values unchanged.


async def send_command(conn, api_id, params=None):  # Send one sport command over the data channel.
    await conn.datachannel.pub_sub.publish_request_new(  # Use the driver's request/response helper.
        COMMAND_TOPIC, {"api_id": api_id, "parameter": params or {}}
    )


def degrees_to_radians(degrees):  # Convert degrees to radians for the tilt API.
    return degrees * math.pi / 180.0  # Return the converted value.


async def countdown(seconds):  # Give a short safety pause before movement starts.
    print(f"Starting in {seconds} seconds...")  # Tell the operator the countdown has begun.
    for remaining in range(seconds, 0, -1):  # Count down one second at a time.
        print(f"{remaining}...")  # Show the remaining time.
        await asyncio.sleep(1)  # Wait one second between updates.


async def run_routine(conn, steps, repeats):  # Run the configured step sequence for the requested number of repeats.
    for repeat_index in range(repeats):  # Loop over the routine the requested number of times.
        for step in steps:  # Run each step in the routine list.
            action = step["action"]  # Read the action name.
            params = step.get("params", {})  # Read any optional parameters.

            if action == "tilt":  # Handle a body tilt step.
                side = params.get("side", "right")  # Read which side should tilt first.
                degrees = params.get("degrees", TILT_ANGLE_DEGREES)  # Read the tilt angle in degrees.
                roll_degrees = degrees if side == "right" else -degrees  # Use a positive roll for right and a negative roll for left.
                await send_command(conn, 1007, {"x": degrees_to_radians(roll_degrees), "y": 0.0, "z": 0.0})  # Send the tilt command.
            else:  # Reject unknown actions so the routine stays predictable.
                raise ValueError(f"Unknown routine action: {action}")  # Explain the issue.

            pause_seconds = step.get("pause", 0.0)  # Read the pause after this step.
            if pause_seconds > 0:  # Only sleep when a pause was requested.
                await asyncio.sleep(pause_seconds)  # Let the pose settle.

        if repeat_index < repeats - 1:  # Skip the between-loop pause after the final repeat.
            await asyncio.sleep(PAUSE_BETWEEN_LOOPS_SECONDS)  # Pause between repeats.


async def main():  # Define the async entry point.
    conn = Go2WebRTCConnection(ROBOT_CONNECTION_METHOD)  # Create the WebRTC connection object.
    await maybe_await(conn.connect())  # Open the connection to the robot.
    try:  # Make sure the robot is sent a sit command even if something fails.
        await countdown(COUNTDOWN_SECONDS)  # Give a short safety countdown before the first motion.
        await run_routine(conn, ROUTINE_STEPS, NUM_REPEATS)  # Run the repeated tilt sequence.
        await send_command(conn, 1009)  # Sit the robot down after all repeats finish.
        await asyncio.sleep(2.0)  # Let the sit-down motion complete.
    finally:  # Clean up the connection whether the routine succeeds or fails.
        disconnect = getattr(conn, "disconnect", None)  # Look for a disconnect method.
        if callable(disconnect):  # Only call it if the library provides one.
            result = disconnect()  # Start the disconnect operation.
            await maybe_await(result)  # Await async disconnects and pass through sync ones.


if __name__ == "__main__":  # Run only when this file is executed directly.
    asyncio.run(main())  # Start the async routine.
