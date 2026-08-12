"""Standalone Go2 Pro example: stand up, happy wag, then sit down."""

import asyncio  # Run async steps in order.

try:
    from go2_webrtc_driver.go2_webrtc_connection import Go2WebRTCConnection, WebRTCConnectionMethod
except ModuleNotFoundError:
    # Newer go2-webrtc-connect exposes these from webrtc_driver.
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod


ROBOT_CONNECTION_METHOD = WebRTCConnectionMethod.LocalAP  # Use the robot's own WiFi hotspot.
ROBOT_API_ID_STAND_UP = 1004  # Sport API ID for standing up.
ROBOT_API_ID_HAPPY_WAG = 1022  # Sport API ID for happy wagging.
ROBOT_API_ID_SIT_DOWN = 1009  # Sport API ID for sitting down.
COMMAND_TOPIC = "rt/api/sport/request"  # Topic used for sport API requests.
COMMAND_ID = 1  # Message identity value used by this simple example.


async def maybe_await(value):  # Await coroutine results and pass through regular return values.
    if asyncio.iscoroutine(value):  # Check whether the value is awaitable.
        return await value  # Await async results.
    return value  # Return plain values unchanged.


async def send_command(conn, api_id, params=None):  # Send one sport command over the data channel.
    await conn.datachannel.pub_sub.publish_request_new(  # Use the driver's request/response helper.
        COMMAND_TOPIC, {"api_id": api_id, "parameter": params or {}}
    )


async def countdown(seconds):  # Pause before movement so the robot starts safely.
    print(f"Starting in {seconds} seconds...")  # Tell the user the countdown has begun.
    for remaining in range(seconds, 0, -1):  # Count down one second at a time.
        print(f"{remaining}...")  # Show the remaining seconds.
        await asyncio.sleep(1)  # Wait one second between updates.


async def main():  # Define the main async control flow.
    conn = Go2WebRTCConnection(ROBOT_CONNECTION_METHOD)  # Create the WebRTC connection object.
    await maybe_await(conn.connect())  # Open the connection to the robot.
    try:  # Ensure the connection is cleaned up even if something fails.
        await countdown(3)  # Give a 3-second safety pause before any motion.
        await send_command(conn, ROBOT_API_ID_STAND_UP)  # Ask the robot to stand up.
        await asyncio.sleep(2)  # Wait for the stand-up motion to complete.
        await send_command(conn, ROBOT_API_ID_HAPPY_WAG)  # Ask the robot to do the happy wag.
        await asyncio.sleep(2)  # Let the happy wag play briefly.
        await send_command(conn, ROBOT_API_ID_SIT_DOWN)  # Ask the robot to sit down.
        await asyncio.sleep(2)  # Give the sit-down motion time to finish.
    finally:  # Run this cleanup code whether the sequence succeeds or fails.
        disconnect = getattr(conn, "disconnect", None)  # Look for a disconnect method if the library provides one.
        if callable(disconnect):  # Only call disconnect when it actually exists.
            result = disconnect()  # Start the disconnect operation.
            await maybe_await(result)  # Await async disconnects and ignore sync ones.


if __name__ == "__main__":  # Only run the script when executed directly.
    asyncio.run(main())  # Start the async main function.
