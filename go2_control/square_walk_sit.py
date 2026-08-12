"""Go2 Pro square walk routine: walk four sides, then sit down."""

import asyncio  # Run the async control flow.

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    # Newer go2-webrtc-connect exposes these from webrtc_driver.
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod


ROBOT_CONNECTION_METHOD = WebRTCConnectionMethod.LocalAP  # Connect through the Go2's own WiFi hotspot.
COMMAND_TOPIC = "rt/api/sport/request"  # Topic used by the sport API.
COMMAND_ID = 1  # Simple message identity for this script.

FORWARD_SPEED_MPS = 0.3  # Keep forward speed at or below 0.3 m/s because of the Lion Cub shell.
FORWARD_WALK_SECONDS = 3.0  # Change this to control the side length of the square.
TURN_RATE_RPS = 0.25  # Conservative left turn rate for an in-place 90 degree turn.
TURN_DURATION_SECONDS = 1.8  # Adjust this if the robot under-turns or over-turns at the corners.


async def maybe_await(value):  # Await coroutine results and pass through regular values.
    if asyncio.iscoroutine(value):  # Check whether the returned value is awaitable.
        return await value  # Await async methods when needed.
    return value  # Return plain values unchanged.


async def send_command(conn, api_id, params=None):  # Send one sport command over the data channel.
    await conn.datachannel.pub_sub.publish_request_new(  # Use the driver's request/response helper.
        COMMAND_TOPIC, {"api_id": api_id, "parameter": params or {}}
    )


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


async def main():  # Define the async entry point.
    conn = Go2WebRTCConnection(ROBOT_CONNECTION_METHOD)  # Create the WebRTC connection object.
    await maybe_await(conn.connect())  # Open the connection to the robot.
    try:  # Keep cleanup in one place.
        await send_command(conn, 1004)  # Stand the robot up before starting the square.
        await asyncio.sleep(2.0)  # Give the stand-up motion time to finish.

        for side_index in range(4):  # Repeat four times to complete the square.
            await walk_for(conn, FORWARD_SPEED_MPS, FORWARD_WALK_SECONDS, turn_rps=0.0)  # Walk one straight side.

            # If the robot turns too far, shorten TURN_DURATION_SECONDS; if it turns too little, lengthen it.
            await walk_for(conn, 0.0, TURN_DURATION_SECONDS, turn_rps=TURN_RATE_RPS)  # Turn left in place for roughly 90 degrees.

        await send_command(conn, 1009)  # Sit the robot down after completing the square.
        await asyncio.sleep(2.0)  # Let the sit-down motion complete.
    finally:  # Clean up the connection whether the routine succeeds or fails.
        disconnect = getattr(conn, "disconnect", None)  # Look for a disconnect method.
        if callable(disconnect):  # Only call it if the library provides one.
            result = disconnect()  # Start the disconnect operation.
            await maybe_await(result)  # Await async disconnects and pass through sync ones.


if __name__ == "__main__":  # Run only when this file is executed directly.
    asyncio.run(main())  # Start the async routine.
