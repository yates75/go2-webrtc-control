#!/bin/bash
# Capped-speed walking/turning via the cli.py sport API.
# Needs roughly 2m x 2m of clear floor space around the robot.
set -e

step () {
    echo
    echo "=== next: $* ==="
    read -p "Press Enter when the robot has clear space and you're watching it... " _
    python -m go2_control.cli "$@"
}

step routine short-walk       # balance-stand -> walk forward ~2s at low speed
step routine turn-left        # in-place-ish turn left
step routine turn-right       # in-place-ish turn right
step routine back-up-slowly   # slow reverse
step routine reset            # stop -> balance-stand -> stop
step stand-down

echo
echo "=== DONE: stage 2 (walking/turning) movement checks complete ==="
