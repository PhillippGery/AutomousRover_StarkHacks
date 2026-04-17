# Dependencies

## ROS2 Humble Packages

Install via apt:

```bash
sudo apt install -y \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-realsense2-camera \
  ros-humble-teleop-twist-joy
```

## Python Packages

```bash
pip3 install pyserial numpy
```

## External ROS2 Repositories

Clone these into `30_ros2_ws/src/` before building:

### Scanse Sweep LIDAR Driver

```bash
cd ~/GUARDIAN/30_ros2_ws/src
git clone https://github.com/107-systems/l3xz_sweep_scanner
```

### LeRobot (HuggingFace)

```bash
cd ~/GUARDIAN/30_ros2_ws/src
git clone https://github.com/huggingface/lerobot
```

Follow the LeRobot README for its own Python dependencies:

```bash
cd ~/GUARDIAN/30_ros2_ws/src/lerobot
pip install -e ".[feetech]"
```

## Full Install (one-shot)

```bash
sudo apt update
sudo apt install -y \
  ros-humble-nav2-bringup \
  ros-humble-robot-localization \
  ros-humble-realsense2-camera \
  ros-humble-teleop-twist-joy

pip3 install pyserial numpy

cd ~/GUARDIAN/30_ros2_ws/src
git clone https://github.com/107-systems/l3xz_sweep_scanner
git clone https://github.com/huggingface/lerobot

cd ~/GUARDIAN/30_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```
