"""Go2 Pro performance routine: sit, stand, tilt, stretch, walk, wave, sit."""

import asyncio  # Run the routine asynchronously.
import math  # Convert degrees to radians for tilt commands.

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    # Newer go2-webrtc-connect exposes these from webrtc_driver.
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod


ROBOT_CONNECTION_METHOD = WebRTCConnectionMethod.LocalAP  # Connect through the Go2's own WiFi hotspot.
COMMAND_TOPIC = "rt/api/sport/request"  # Topic used by the sport API.
COMMAND_ID = 1  # Simple message identity for this routine.

FORWARD_SPEED_MPS = 0.3  # Keep forward motion at or below 0.3 m/s for the Lion Cub shell.
PERFORMANCE_DURATION_SECONDS = 90.0  # Change this to your X-second performance length.
TILT_ANGLE_DEGREES = 12.0  # A small, expressive tilt for the curious head movement.
TURN_RATE_RPS = 0.2  # A conservative turn rate for the walk-forward-and-back section.

ROUTINE_STEPS = [
    # The curtain opens and the robot begins sitting quietly, ready for the performance.
    {"action": "sit", "pause": 1.0},

    # The robot rises slowly and carefully so the performance starts with a calm first beat.
    {"action": "stand_up", "pause": 2.0},

    # The robot looks curious by tilting gently to the left.
    {"action": "tilt", "params": {"roll": TILT_ANGLE_DEGREES}, "pause": 1.0},

    # The robot answers its own curiosity by tilting gently to the right.
    {"action": "tilt", "params": {"roll": -TILT_ANGLE_DEGREES}, "pause": 1.0},

    # The robot repeats the curious leftward tilt for a second expressive beat.
    {"action": "tilt", "params": {"roll": TILT_ANGLE_DEGREES}, "pause": 1.0},

    # The robot repeats the curious rightward tilt to complete the pair.
    {"action": "tilt", "params": {"roll": -TILT_ANGLE_DEGREES}, "pause": 1.0},

    # The robot stretches like it is warming up before the next scene.
    {"action": "stretch", "pause": 2.0},

    # The robot walks forward in a controlled line to show a clean, confident motion.
    {"action": "walk", "params": {"forward": FORWARD_SPEED_MPS, "turn": 0.0}, "duration": 4.0, "pause": 0.5},

    # The robot turns while moving at a gentle rate so the audience sees a smooth arc.
    {"action": "walk", "params": {"forward": FORWARD_SPEED_MPS, "turn": TURN_RATE_RPS}, "duration": 2.5, "pause": 0.5},

    # The robot walks back forward again to reset the stage picture.
    {"action": "walk", "params": {"forward": FORWARD_SPEED_MPS, "turn": 0.0}, "duration": 4.0, "pause": 0.5},

    # The robot waves hello as a friendly finish before the final bow.
    {"action": "hello", "pause": 2.0},

    # The robot stops cleanly so the finale ends under control.
    {"action": "stop", "pause": 0.5},

    # The robot sits down to close the performance calmly and neatly.
    {"action": "sit", "pause": 2.0},
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
    print(f"Starting performance in {seconds} seconds...")  # Tell the operator the countdown has begun.
    for remaining in range(seconds, 0, -1):  # Count down one second at a time.
        print(f"{remaining}...")  # Show the remaining time.
        await asyncio.sleep(1)  # Wait one second between updates.


async def walk_for(conn, forward_mps, duration_s, turn_rps=0.0, interval_s=0.1):  # Repeatedly send move commands for a duration.
    if duration_s <= 0:  # Validate the duration.
        raise ValueError("duration_s must be greater than 0.")  # Explain the issue.
    if abs(forward_mps) > FORWARD_SPEED_MPS:  # Keep the robot within the shell-safe speed limit.
        raise ValueError("forward_mps must be 0.3 m/s or below.")  # Explain the issue.
    end_time = asyncio.get_running_loop().time() + duration_s  # Compute the stop time.
    try:  # Ensure the robot gets a stop command even if something fails.
        while asyncio.get_running_loop().time() < end_time:  # Keep moving until the requested time ends.
            await send_command(conn, 1008, {"x": forward_mps, "y": 0.0, "z": turn_rps})  # Send one motion update.
            await asyncio.sleep(interval_s)  # Pause briefly before the next update.
    finally:  # Always stop the robot after the motion loop.
        await send_command(conn, 1003)  # Tell the robot to stop moving.


async def run_routine(conn, steps):  # Run a list of step dictionaries in order.
    for step in steps:  # Process each step in sequence.
        action = step["action"]  # Read the action name.
        params = step.get("params", {})  # Read the optional parameters.

        if action == "sit":  # Sit the robot down.
            await send_command(conn, 1009)  # Send the sit command.
        elif action == "stand_up":  # Stand the robot up.
            await send_command(conn, 1004)  # Send the stand-up command.
        elif action == "tilt":  # Tilt the body left or right for a curious gesture.
            roll_degrees = params.get("roll", 0.0)  # Read the roll in degrees.
            await send_command(conn, 1007, {"x": degrees_to_radians(roll_degrees), "y": 0.0, "z": 0.0})  # Convert and send the tilt.
        elif action == "stretch":  # Stretch the robot for a warm-up pose.
            await send_command(conn, 1017)  # Send the stretch command.
        elif action == "walk":  # Walk for a fixed time with optional turning.
            forward = params.get("forward", FORWARD_SPEED_MPS)  # Read the forward speed.
            turn = params.get("turn", 0.0)  # Read the turn rate.
            await walk_for(conn, forward, step["duration"], turn_rps=turn)  # Walk for the requested duration.
        elif action == "hello":  # Wave hello to the audience.
            await send_command(conn, 1016)  # Send the hello command.
        elif action == "stop":  # Stop all motion before the ending pose.
            await send_command(conn, 1003)  # Send the stop command.
        else:  # Reject unknown actions early.
            raise ValueError(f"Unknown routine action: {action}")  # Explain the problem.

        pause_seconds = step.get("pause", 0.0)  # Read the requested pause after the action.
        if pause_seconds > 0:  # Only sleep when a pause was requested.
            await asyncio.sleep(pause_seconds)  # Let the pose or motion settle.


async def main():  # Define the async entry point for the routine.
    conn = Go2WebRTCConnection(ROBOT_CONNECTION_METHOD)  # Create the WebRTC connection object.
    await maybe_await(conn.connect())  # Open the connection to the robot.
    try:  # Keep cleanup in one place.
        await countdown(3)  # Give a short safety countdown before motion.
        await send_command(conn, 1002)  # Ask the robot to balance before starting the performance.
        await asyncio.sleep(1.0)  # Give the balance command a moment to settle.
        await run_routine(conn, ROUTINE_STEPS)  # Run the full performance routine.
    finally:  # Clean up regardless of how the routine ends.
        disconnect = getattr(conn, "disconnect", None)  # Look for a disconnect method.
        if callable(disconnect):  # Only call it if it exists.
            result = disconnect()  # Start the disconnect operation.
            await maybe_await(result)  # Await async disconnects and pass through sync ones.


if __name__ == "__main__":  # Run only when the file is executed directly.
    asyncio.run(main())  # Start the async routine.
