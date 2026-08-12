#!/bin/bash
# Passive/log-only checks: reads the robot's camera + lidar and writes
# CSV/JPEG output. None of these send movement commands.
set -x
echo "=== remote_input (physical remote passthrough, read-only) ==="
python -m go2_control.remote_input --count 5
sleep 5

echo "=== object_tracker (YOLO camera detection, passive, logs only) ==="
python -m go2_control.object_tracker --count 5 --interval 0.5 --out-csv /tmp/object_track.csv
sleep 5

echo "=== lidar_tracker (lidar clustering, passive, logs only) ==="
python -m go2_control.lidar_tracker --calibrate-frames 5 --count 5 --out-csv /tmp/lidar_track.csv

echo "=== DONE ==="
