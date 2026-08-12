#!/bin/bash
# In-place movement checks only: stand up, gesture animations, stand down.
# No walking. Pauses before each step so you can watch and Ctrl-C if needed.
set -e

step () {
    echo
    echo "=== next: $* ==="
    read -p "Press Enter when the robot has clear space and you're watching it... " _
    python -m go2_control.cli "$@"
}

step routine calm-start   # balance-stand -> stand-up -> stop (in place)
step hello
step content
step heart-pose
step stretch
step stand-down

echo
echo "=== DONE: stage 1 (in-place) movement checks complete ==="
