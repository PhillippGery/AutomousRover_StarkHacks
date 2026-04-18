# GUARDIAN ROS2 Workspace

ROS2 Humble workspace using `ament_python` (pure Python — no C++, no CMakeLists.txt).

## Packages

| Package | Owner | Purpose |
|---------|-------|---------|
| [guardian_bringup](src/guardian_bringup/) | Phillipp | Launch files, EKF config, Nav2 config |
| [guardian_description](src/guardian_description/) | Phillipp | URDF/xacro robot model |
| [guardian_drive](src/guardian_drive/) | Phillipp | Mecanum kinematics + Arduino serial bridge |
| [guardian_localization](src/guardian_localization/) | Phillipp | LIDAR republisher, sensor prep for Nav2 |
| [guardian_arms](src/guardian_arms/) | Dipam | Dual SO-101 arm management + LeRobot bridge |
| [guardian_teleop](src/guardian_teleop/) | Victor | Quest 3 + joystick teleoperation |

## Build

```bash
cd ~/GUARDIAN
source /opt/ros/jazzy/setup.bash
cd 30_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Or use the convenience script:

```bash
bash ~/GUARDIAN/60_scripts/build_workspace.sh
```
