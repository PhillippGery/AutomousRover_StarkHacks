# GUARDIAN
### Autonomous Confined Space Intervention Robot

*StarkHacks 2026 | Purdue University | April 17–19, 2026*

![ROS2 Jazzy](https://img.shields.io/badge/ROS2-Jazzy-blue)
![Python 3.12](https://img.shields.io/badge/Python-3.12-green)
![ESP32](https://img.shields.io/badge/ESP32-Feather_V2-teal)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)

GUARDIAN is an autonomous mobile manipulation system that enables remote operators to navigate to hazardous confined spaces and physically intervene using dual robotic arms and mixed reality — without ever entering the space.

---

## Table of Contents

- [Overview](#overview)
- [Hardware](#hardware)
- [Software](#software)
- [Quick Start](#quick-start)
- [Team](#team)
- [License](#license)

---

## Overview

GUARDIAN (**G**round **U**nit for **A**utonomous **R**econnaissance, **D**istal **I**ntervention, and **A**rm **N**avigation) is a four-wheeled omnidirectional rover equipped with dual SO-101 robotic arms, indoor localization via Intel RealSense T265 + EKF, Nav2 autonomous navigation, and a Meta Quest 3 mixed reality operator interface. It is designed to enter confined or hazardous spaces where a human cannot safely operate.

---

## Hardware

### System Requirements

| Item | Requirement |
|------|-------------|
| OS | Ubuntu 24.04 LTS |
| ROS2 | Jazzy Jalisco |
| Python | 3.12+ |
| Compute | AMD Ryzen AI MiniPC |

### Hardware Overview

| Component | Model | Role |
|-----------|-------|------|
| Compute | AMD Ryzen AI MiniPC | ROS2 master, AI inference |
| Arms | SO-101 LeRobot ×2 | Dual manipulation |
| Tracking | Intel RealSense T265 | Indoor V-SLAM localization |
| LIDAR | Scanse Sweep V1 | 360° obstacle detection |
| Drive | JGB37-3530 ×4 + Mecanum ×4 | Omnidirectional movement |
| Motor ctrl | ESP32 Feather V2 ×2 | Low-level PID, LEFT+RIGHT split |
| Interface | Meta Quest 3 | MR teleoperation |

---

## Software

### Repository Structure

| Folder | Contents |
|--------|----------|
| [10_docs/](10_docs/) | Architecture, hardware docs, setup guides |
| [20_hardware/](20_hardware/) | CAD files, Arduino motor controller sketch |
| [30_ros2_ws/](30_ros2_ws/) | ROS2 Humble workspace (5 packages) |
| [40_lerobot/](40_lerobot/) | LeRobot configs, training datasets, policies |
| [50_teleop/](50_teleop/) | Meta Quest 3 WebSocket bridge |
| [60_scripts/](60_scripts/) | Setup, build, and run shell scripts |
| [70_media/](70_media/) | Demo videos, photos, screenshots |

### ROS2 Packages

| Package | Purpose |
|---------|---------|
| `guardian_bringup` | Launch files and system configs |
| `guardian_description` | URDF/xacro robot model |
| `guardian_drive` | Mecanum kinematics + Arduino serial bridge |
| `guardian_localization` | LIDAR republisher, sensor prep |
| `guardian_arms` | Dual SO-101 arm management + LeRobot bridge |
| `guardian_teleop` | Quest 3 + joystick teleoperation |

---

## Quick Start

```bash
git clone https://github.com/PhillippGery/GUARDIAN.git
cd GUARDIAN/30_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
ros2 launch guardian_bringup guardian_full.launch.py
```

Or use the convenience script:

```bash
cd GUARDIAN
bash 60_scripts/run_guardian.sh
```

---

## Team

| Member | Role |
|--------|------|
| Phillipp Gery | ROS2 architecture, Nav2, EKF, mecanum kinematics |
| Vedant | Arduino low-level control, PID, encoder odometry |
| Dipam | Both SO-101 arms, LeRobot training, arm integration |
| Victor | Chassis CAD/build, power system, Quest interface |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 GUARDIAN Team — StarkHacks 2026, Purdue University
