#!/bin/bash
# MIT License
# GUARDIAN — StarkHacks 2026
# Script: run_guardian.sh
# Purpose: interactive launch menu

set -e

source /opt/ros/jazzy/setup.bash
source "$(dirname "$0")/../30_ros2_ws/install/setup.bash"

echo ""
echo "========================================"
echo "  GUARDIAN Launch Menu"
echo "  StarkHacks 2026 | Purdue University"
echo "========================================"
echo "  1) Full autonomous mode"
echo "  2) Teleop only"
echo "  3) Arms only"
echo "  4) Motor test"
echo "========================================"
read -rp "Select [1-4]: " choice

case $choice in
  1)
    echo "Launching full autonomous mode..."
    ros2 launch guardian_bringup guardian_full.launch.py
    ;;
  2)
    echo "Launching teleop mode..."
    ros2 launch guardian_bringup guardian_teleop.launch.py
    ;;
  3)
    echo "TODO: arms-only launch not yet implemented"
    # ros2 launch guardian_arms guardian_arms.launch.py
    ;;
  4)
    echo "TODO: motor test script not yet implemented"
    # ros2 run guardian_drive serial_bridge_node --ros-args -p test_mode:=true
    ;;
  *)
    echo "Invalid selection: $choice"
    exit 1
    ;;
esac
