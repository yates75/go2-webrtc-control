"""Go2 Pro sequence: stand up, walk, turn, walk, then sit down."""

import asyncio  # Run the async control flow.

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    # Newer go2-webrtc-connect exposes these from webrtc_driver.
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod


ROBOT_CONNECTION_METHOD = WebRTCConnectionMethod.LocalAP  # Connect through the Go2's own WiFi hotspot.
API_ID_STAND_UP = 1004  # Sport API ID for standing up.
API_ID_MOVE = 1008  # Sport API ID for walking.
API_ID_STOP_MOVE = 1003  # Sport API ID for stopping motion.
API_ID_SIT = 1009  # Sport API ID for sitting down.
COMMAND_TOPIC = "rt/api/sport/request"  # Topic used for sport requests.
COMMAND_ID = 1  # Simple message identity value for this script.

FORWARD_SPEED_MPS = 0.3  # Keep forward speed at or below 0.3 m/s for the Lion Cub shell.
FIRST_WALK_SECONDS = 3.0  # Replace this with your X value.
TURN_SECONDS = 2.0  # Replace this with your Y value.
SECOND_WALK_SECONDS = 3.0  # Replace this with your X value again.

# Use a positive turn rate for left turns and a negative turn rate for right turns.
# Gentle turns are usually around 0.15 to 0.25 rad/s.
# Sharper turns are usually around 0.40 to 0.70 rad/s.
TURN_DIRECTION = "left"  # Change this to "right" if you want the opposite direction.
TURN_RATE_RPS = 0.20  # Gentle left turn; use about -0.20 for a gentle right turn.


async def maybe_await(value):  # Await coroutine results and pass through regular values.
    if asyncio.iscoroutine(value):  # Check whether the returned value is awaitable.
        return await value  # Await async methods when needed.
    return value  # Return plain values unchanged.


async def send_command(conn, api_id, params=None):  # Send one sport command to the robot.
    await conn.datachannel.pub_sub.publish_request_new(  # Use the driver's request/response helper.
        COMMAND_TOPIC, {"api_id": api_id, "parameter": params or {}}
    )


def clamp_turn_rate(turn_rate_rps):  # Keep turn rates conservative for the shell.
    if abs(turn_rate_rps) > 0.7:  # Reject overly aggressive turns.
        raise ValueError("TURN_RATE_RPS should stay between -0.7 and 0.7 for safe, conservative control.")  # Explain the limit.
    return turn_rate_rps  # Return the accepted rate.


def turn_rate_for_direction(direction, magnitude):  # Convert direction plus magnitude into a signed turn rate.
    if direction.lower() == "left":  # Left turns use a positive rate.
        return abs(magnitude)  # Return a positive value.
    if direction.lower() == "right":  # Right turns use a negative rate.
        return -abs(magnitude)  # Return a negative value.
    raise ValueError('TURN_DIRECTION must be "left" or "right".')  # Reject invalid directions.


async def walk_for(conn, forward_mps, duration_s, turn_rps=0.0, interval_s=0.1):  # Keep sending move commands for a period of time.
    if duration_s <= 0:  # Validate the duration.
        raise ValueError("duration_s must be greater than 0.")  # Explain the issue.
    if abs(forward_mps) > 0.3:  # Enforce the shell safety speed cap.
        raise ValueError("forward_mps must be 0.3 m/s or below.")  # Explain the issue.
    end_time = asyncio.get_running_loop().time() + duration_s  # Compute the stop time.
    try:  # Ensure the robot gets a stop command even if something fails.
        while asyncio.get_running_loop().time() < end_time:  # Keep moving until the requested duration expires.
            await send_command(conn, API_ID_MOVE, {"x": forward_mps, "y": 0.0, "z": turn_rps})  # Send one motion update.
            await asyncio.sleep(interval_s)  # Pause briefly before the next update.
    finally:  # Always stop the robot after the loop.
        await send_command(conn, API_ID_STOP_MOVE)  # Tell the robot to stop moving.


async def main():  # Define the main async control flow.
    conn = Go2WebRTCConnection(ROBOT_CONNECTION_METHOD)  # Create the connection object.
    await maybe_await(conn.connect())  # Open the WebRTC connection.
    try:  # Keep cleanup in one place.
        await send_command(conn, API_ID_STAND_UP)  # Step 1: stand up.
        await asyncio.sleep(2.0)  # Give the stand-up motion time to finish.

        await walk_for(conn, FORWARD_SPEED_MPS, FIRST_WALK_SECONDS, turn_rps=0.0)  # Step 2: walk forward.

        signed_turn_rate = clamp_turn_rate(turn_rate_for_direction(TURN_DIRECTION, TURN_RATE_RPS))  # Convert the chosen direction into a signed vz value.
        await walk_for(conn, FORWARD_SPEED_MPS, TURN_SECONDS, turn_rps=signed_turn_rate)  # Step 3: turn while moving.

        await walk_for(conn, FORWARD_SPEED_MPS, SECOND_WALK_SECONDS, turn_rps=0.0)  # Step 4: walk forward again.

        await send_command(conn, API_ID_STOP_MOVE)  # Step 5: stop before sitting down.
        await asyncio.sleep(0.5)  # Give the stop command a moment to register.
        await send_command(conn, API_ID_SIT)  # Step 5: sit down.
        await asyncio.sleep(2.0)  # Let the sit-down motion finish.
    finally:  # Clean up the connection no matter what happens above.
        disconnect = getattr(conn, "disconnect", None)  # Look for a disconnect method.
        if callable(disconnect):  # Only call it if the library provides one.
            result = disconnect()  # Start the disconnect operation.
            await maybe_await(result)  # Await async disconnects and pass through sync ones.


if __name__ == "__main__":  # Run only when this file is executed directly.
    asyncio.run(main())  # Start the async script.
