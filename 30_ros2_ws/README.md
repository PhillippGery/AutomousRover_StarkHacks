# GUARDIAN ROS2 Workspace

ROS2 Jazzy workspace — Ubuntu 24.04, pure Python (ament_python).

## Packages

| Package | Owner | Purpose |
|---------|-------|---------|
| [guardian_bringup](src/guardian_bringup/) | Phillipp | Launch files, EKF config, Nav2 config |
| [guardian_description](src/guardian_description/) | Phillipp | URDF/xacro robot model |
| [guardian_drive](src/guardian_drive/) | Phillipp | Mecanum kinematics + ESP32 serial bridge |
| [guardian_localization](src/guardian_localization/) | Phillipp | LIDAR republisher, sensor prep for Nav2 |
| [guardian_arms](src/guardian_arms/) | Dipam | Dual SO-101 arm management + LeRobot bridge |
| [guardian_teleop](src/guardian_teleop/) | Victor | Quest 3 + joystick + keyboard teleoperation |

---

## Build

```bash
cd ~/AutomousRover_StarkHacks/30_ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

Build a single package:
```bash
colcon build --packages-select <package_name>
```

---

## Keyboard Teleop (WASD)

> Requires ESP32 connected on `/dev/ttyACM0`

```bash
cd ~/AutomousRover_StarkHacks/30_ros2_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch guardian_bringup guardian_teleop.launch.py
```

Controls:
| Key | Action |
|-----|--------|
| `w` | Forward |
| `s` | Backward |
| `a` | Strafe left |
| `d` | Strafe right |
| `q` | Rotate left |
| `e` | Rotate right |
| `space` | Stop |
| `x` | Quit |

---

## LIDAR

> Requires Scanse Sweep connected via USB (FTDI adapter)

```bash
cd ~/AutomousRover_StarkHacks/30_ros2_ws
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch l3xz_sweep_scanner laser.py
```

Visualize in RViz (open a new terminal):
```bash
source /opt/ros/jazzy/setup.bash
rviz2 --display-config /home/aup/AutomousRover_StarkHacks/30_ros2_ws/src/l3xz_sweep_scanner/rviz/laser.rviz
```

Check LIDAR topic:
```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 topic echo /l3xz/laser --once
```

---

## Check Connected Hardware

```bash
# All USB devices
lsusb

# Serial ports (ESP32 = ttyACM0, LIDAR = ttyUSB0)
ls /dev/ttyUSB* /dev/ttyACM*

# Camera
ls /dev/video*
```

---

## Useful ROS2 Debug Commands

```bash
# List all active topics
ros2 topic list

# Monitor cmd_vel
ros2 topic echo /cmd_vel

# Monitor wheel RPM
ros2 topic echo /wheel_rpm

# Monitor odometry
ros2 topic echo /odom

# List active nodes
ros2 node list
```
