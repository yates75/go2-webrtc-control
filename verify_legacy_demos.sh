#!/bin/bash
# Standalone example/demo scripts that talk to the driver directly
# (bypassing client.py) -- good regression coverage for the patched
# handshake specifically. All of these move the robot.
# square_walk_sit.py needs the most space: roughly a 1m x 1m clear square.
set -e

step () {
    echo
    echo "=== next: python -m go2_control.$1 ==="
    read -p "Press Enter when the robot has clear space and you're watching it... " _
    python -m "go2_control.$1"
}

step stand_wag_sit_example   # stand up, happy wag, sit down
step repeat_tilt_sit         # tilt one way, then the other, then sit
step walk_turn_walk_sit      # stand, walk, turn, walk, sit
step performance_routine     # sit, stand, tilt, stretch, walk, wave, sit
step square_walk_sit         # walk a full square, then sit (needs the most room)

echo
echo "=== DONE: legacy demo scripts complete ==="
