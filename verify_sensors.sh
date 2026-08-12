#!/bin/bash
set -x
echo "=== telemetry (state, 5 messages) ==="
python -m go2_control.telemetry state --count 5
sleep 5
echo "=== camera_view (3 frames) ==="
python -m go2_control.camera_view --count 3 --interval 0.5
sleep 5
echo "=== lidar_view (5 messages) ==="
python -m go2_control.lidar_view --count 5
sleep 5
echo "=== audio list (no playback) ==="
python -m go2_control.audio list
echo "=== DONE ==="
