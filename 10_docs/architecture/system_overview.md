# System Overview

## Four-Layer Architecture

| Layer | Components | Responsibilities |
|-------|-----------|-----------------|
| **Operator** | Meta Quest 3, SO-101 Leader Arms ×2 | Mixed reality view, hand tracking, leader arm teleoperation |
| **Brain** | AMD Ryzen AI MiniPC, ROS2 Humble | Nav2 planning, EKF localization, LeRobot inference, mecanum kinematics |
| **Motor Control** | Arduino Mega, L298N ×2 | Per-wheel PID, encoder feedback, PWM output |
| **Chassis** | JGB37-3530 ×4, Mecanum wheels ×4 | Omnidirectional movement |

## Communication Flow

```
[Meta Quest 3] ──────────────────────────────┐
[SO-101 Leader Arms ×2] ──────────────────┐  │
                                           ▼  ▼
                              ┌─────────────────────────┐
                              │   AMD Ryzen AI MiniPC   │
                              │      ROS2 Humble        │
                              │  Nav2 | EKF | LeRobot   │
                              │  Mecanum Kinematics      │
                              └────────────┬────────────┘
                                           │ USB Serial
                              ┌────────────▼────────────┐
                              │      Arduino Mega        │
                              │   PID ×4 | L298N ×2     │
                              └──┬──────┬──────┬──────┬─┘
                                 ▼      ▼      ▼      ▼
                               FL    FR    BL    BR
                            [JGB37-3530 encoder motors ×4]
                            [Mecanum wheels ×4]
```

## Why No GPS?

GUARDIAN operates indoors in confined spaces — GPS signals are unavailable or unreliable in these environments. Instead, localization is achieved through sensor fusion:

| Sensor | Topic | Contribution |
|--------|-------|-------------|
| Intel RealSense T265 | `/camera/odom/sample` | Visual-inertial odometry, primary pose source |
| Wheel encoders | `/odom` | Short-term dead reckoning between visual frames |
| MPU-6050 IMU | `/imu/data` | Orientation estimate, slip/tilt detection |
| Scanse Sweep LIDAR | `/scan` | Obstacle detection, optional scan-matching |

All sources are fused by `robot_localization` EKF running at 50 Hz, producing a single `/odometry/filtered` topic used by Nav2.

## Sensor Fusion Table

| Sensor | Topic | Frequency | Role in EKF |
|--------|-------|-----------|-------------|
| Intel RealSense T265 | `/camera/odom/sample` | 30 Hz | Primary pose, handles long-term drift |
| Wheel encoders (via Arduino) | `/odom` | 50 Hz | Short-term dead reckoning |
| MPU-6050 6-axis IMU | `/imu/data` | 100 Hz | Orientation, slip detection |
| Scanse Sweep V1 LIDAR | `/scan` | 5 Hz | Obstacle avoidance, optional SLAM |

> **Note:** The GY-NEO6MV2 GPS module is available in the hardware kit but is **not used** — the indoor environment provides no GPS signal. It is kept as a hardware reserve for future outdoor missions.
