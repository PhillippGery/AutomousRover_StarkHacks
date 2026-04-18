# GUARDIAN ROS2 Workspace

ROS2 Jazzy workspace — Ubuntu 24.04, pure Python (ament_python).

## Packages

| Package | Owner | Purpose |
|---------|-------|---------|
| [guardian_bringup](src/guardian_bringup/) | Phillipp | Launch files, EKF config, Nav2 config |
| [guardian_description](src/guardian_description/) | Phillipp | URDF/xacro robot model + Gazebo sim world |
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

## Hardware Setup

### ESP32 Serial Ports

| Port | Board | Motors |
|------|-------|--------|
| `/dev/ttyACM0` | LEFT ESP32 | M1 = Front-Left, M2 = Rear-Left |
| `/dev/ttyACM1` | RIGHT ESP32 | M1 = Front-Right, M2 = Rear-Right |
| `/dev/ttyUSB0` | Scanse Sweep LIDAR | FTDI adapter |

### ESP32 Serial Protocol

- Host → ESP32: `M1:<rpm> M2:<rpm>\n` (float RPM values)
- ESP32 → Host: `ENC:M1:<ticks> M2:<ticks>\n` (cumulative ticks, every 50ms)
- CPR = 175 (700 ticks/rev gearbox ÷ 4, RISING-edge single-channel)
- Safety stop: motors halt if no command received for 2000ms

### Motor Specs (FIT0186 / DFRobot GB37Y3530-12V-251R)

| Parameter | Value |
|-----------|-------|
| Gear ratio | 43.8:1 |
| No-load RPM | 251 RPM |
| Encoder CPR | 175 ticks/rev (effective) |
| Start voltage | 1V (low-speed capable) |
| Wheel radius | 74.8 mm |

### Lidar Reset (if node crashes on startup)

The Scanse Sweep segfaults if left in data-streaming mode. Reset before launching:

```bash
stty -F /dev/ttyUSB0 115200 && printf 'DX\n' > /dev/ttyUSB0 && sleep 1 && printf 'RR\n' > /dev/ttyUSB0 && sleep 3
```

---

## Launch Files

| Launch | Purpose | Hardware needed |
|--------|---------|-----------------|
| `guardian_teleop.launch.py` | Drive with keyboard only | ESP32s |
| `guardian_mapping.launch.py` | Drive + LIDAR + SLAM mapping | ESP32s + Sweep |
| `guardian_sim.launch.py` | Full Gazebo simulation | None |
| `guardian_nav.launch.py` | Full Nav2 stack | ESP32s + Sweep |

---

## Mapping (Real Robot)

> Requires ESP32s on ttyACM0/1 and Scanse Sweep on ttyUSB0

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch guardian_bringup guardian_mapping.launch.py
```

Drive around with the keyboard (opens in xterm). Map builds in RViz automatically.
SLAM params: `minimum_travel_distance: 0.0` — map updates even when stationary.

---

## Gazebo Simulation + Autonomous Navigation

> No hardware required — full sim with SLAM, Nav2, and keyboard teleop

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch guardian_bringup guardian_sim.launch.py
```

### What launches
- Gazebo Harmonic: 10×10m walled room with 3 box obstacles
- Robot spawns at origin after ~3s
- `/scan` from GPU lidar, `/odom` + `/tf` from DiffDrive plugin
- SLAM Toolbox starts mapping at ~5s
- All Nav2 nodes start at ~10s (`autostart: False` — wait for manual trigger)
- RViz opens with SLAM map, costmaps, global/local path displays
- Teleop keyboard opens in xterm window

### Startup procedure
1. Wait ~12 seconds for everything to load
2. In the **RViz Nav2 panel**, click **"Startup"** button **once**
3. Watch terminal for: `[lifecycle_manager_navigation]: Managed nodes bringup complete`
4. Nav2 panel shows **Navigation: active** and **Localization: active**

### Build the map first
Drive around with the keyboard to build the SLAM map before sending Nav2 goals.

### Send an autonomous navigation goal
1. Click the **Nav2 Goal** tool (green arrow) in the RViz toolbar
2. Click a position on the map and drag to set heading
3. Release — robot drives autonomously, avoiding obstacles

Verify:
```bash
ros2 topic hz /scan    # ~5Hz
ros2 topic hz /odom    # ~50Hz
ros2 topic hz /map     # ~1Hz
ros2 topic echo /plan --once | head -5   # path published when goal set
ros2 topic echo /cmd_vel | head -5       # velocities while navigating
```

### Nav2 config notes
- `autostart: False` — prevents double-bringup (first auto + user click = conflict)
- `bond_timeout: 0.0` — disables heartbeat bonds (sim clock vs wall clock mismatch)
- `wait_for_service_timeout: 3000` — gives behavior_server 3s to come up before bt_navigator connects
- Behavior plugin named `backup` (no underscore) — matches what default BT XML expects (`/backup` action server)
- `behavior_plugins: ['spin', 'backup', 'drive_on_heading', 'wait', 'assisted_teleop']`

---

## SLAM Toolbox Key Parameters

Configured in `src/guardian_bringup/config/nav2_params.yaml`:

| Parameter | Value | Why |
|-----------|-------|-----|
| `minimum_travel_distance` | 0.0 | Map updates even when stationary |
| `minimum_travel_heading` | 0.0 | Map updates without rotation |
| `map_update_interval` | 1.0 s | Fast map refresh |
| `max_laser_range` | 8.0 m | Matches Scanse Sweep range |

**Important:** The SLAM launch argument must be `slam_params_file` (not `params_file`) — this is the key that `online_async_launch.py` actually reads.

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
