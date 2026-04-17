#!/bin/bash
# MIT License
# GUARDIAN — StarkHacks 2026
# Script: setup_amd_minipc.sh
# Purpose: one-shot install of all system dependencies on Ubuntu 22.04

set -e

echo "========================================"
echo "  GUARDIAN AMD MiniPC Setup"
echo "  StarkHacks 2026"
echo "========================================"

# ─── ROS2 Humble ──────────────────────────────────────────────────────────────
echo "[1/5] Installing ROS2 Humble..."

sudo apt update
sudo apt install software-properties-common curl -y

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install ros-humble-desktop -y
sudo apt install python3-colcon-common-extensions python3-rosdep -y

sudo rosdep init || true  # ignore error if already initialized
rosdep update

# ─── ROS2 Packages ────────────────────────────────────────────────────────────
echo "[2/5] Installing ROS2 packages..."

sudo apt install -y \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-realsense2-camera \
  ros-humble-teleop-twist-joy

# ─── Python Packages ──────────────────────────────────────────────────────────
echo "[3/5] Installing Python packages..."

pip3 install pyserial numpy websockets

# ─── Intel RealSense udev rules ───────────────────────────────────────────────
echo "[4/5] Setting up Intel RealSense udev rules..."

sudo apt install -y librealsense2-utils librealsense2-dev || \
  echo "Warning: librealsense2 not found in apt — install manually from Intel repo"

# ─── Serial port permissions ──────────────────────────────────────────────────
echo "[5/5] Adding user to dialout group for serial access..."

sudo usermod -aG dialout "$USER"
echo "Note: log out and back in for dialout group to take effect"

# ─── ROS2 source in bashrc ────────────────────────────────────────────────────
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
  echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
  echo "Added ROS2 Humble to ~/.bashrc"
fi

echo ""
echo "========================================"
echo "  Setup complete!"
echo "  Next steps:"
echo "  1. Log out and back in (dialout group)"
echo "  2. Run: bash 60_scripts/build_workspace.sh"
echo "  3. Run: bash 60_scripts/run_guardian.sh"
echo "========================================"
