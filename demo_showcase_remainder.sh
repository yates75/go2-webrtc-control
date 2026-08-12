#!/bin/bash
set -x
echo "=== record lidar (5 frames) ==="
python -m go2_control.lidar_view --count 5 --record --out-dir lidar_recording
sleep 5

echo "=== play a sound ==="
python -m go2_control.audio play --id 2bdc8af0-2107-421a-a0cf-1f1b833159a1
echo "=== DONE ==="
