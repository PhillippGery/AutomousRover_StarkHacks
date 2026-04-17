# Indoor Localization & Sensor Fusion

## Why Each Sensor

GUARDIAN operates entirely indoors where GPS is unavailable. Reliable pose estimation requires fusing multiple complementary sensors:

| Sensor | Why Needed | What It Contributes |
|--------|------------|-------------------|
| **Intel RealSense T265** | Primary localization — handles long-term drift | Visual-inertial odometry at 30 Hz, 6-DoF pose |
| **Wheel Encoders** | Bridge between visual frames | Dead reckoning at 50 Hz, captures short motions |
| **MPU-6050 IMU** | Orientation ground truth | Yaw/pitch/roll at 100 Hz, detects wheel slip and tilt |
| **Scanse Sweep LIDAR** | Environmental awareness | 360° scan at 5 Hz, obstacle detection + optional scan-matching |

## EKF Input Configuration

All sources feed `robot_localization` EKF node (config: `30_ros2_ws/src/guardian_bringup/config/ekf_params.yaml`):

| Source | ROS2 Topic | Msg Type | Hz | Contribution |
|--------|-----------|----------|----|-------------|
| T265 Visual-Inertial | `/camera/odom/sample` | `nav_msgs/Odometry` | 30 | Primary pose, handles drift |
| Encoder Odometry | `/odom` | `nav_msgs/Odometry` | 50 | Short-term dead reckoning |
| MPU-6050 | `/imu/data` | `sensor_msgs/Imu` | 100 | Orientation, slip detection |
| Sweep LIDAR | `/scan` | `sensor_msgs/LaserScan` | 5 | Obstacle avoidance, optional SLAM |

## EKF State Vector

The EKF operates in 2D mode (`two_d_mode: true`) since GUARDIAN is a ground vehicle:

```
State: [x, y, yaw, vx, vy, vyaw, ax]
```

- Position (x, y) from T265 + encoders
- Yaw from T265 + IMU
- Velocities from encoders + IMU differentiation

## GPS Reserve Note

> The **GY-NEO6MV2 NEO-6M GPS module** is present in the hardware kit but is **not used** in this deployment. The indoor/confined space environment provides no satellite signal. It is retained as a hardware reserve for potential future outdoor missions.
