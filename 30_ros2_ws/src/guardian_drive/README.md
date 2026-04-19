# guardian_drive

**Owner: Phillipp**

Mecanum wheel kinematics and Arduino serial bridge.

## Nodes

| Node | Purpose |
|------|---------|
| `guardian_drive_node` | Installed alias for the serial bridge used by `guardian_real.launch` |
| `mecanum_kinematics_node` | Converts `/cmd_vel` Twist → 4× wheel RPM targets |
| `serial_bridge_node` | Sends RPM targets to Arduino, reads encoder feedback, publishes `/odom` |

## Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/cmd_vel` | `geometry_msgs/Twist` | Subscribed |
| `/wheel_rpms` | `std_msgs/Float32MultiArray` | Published (FL, FR, BL, BR) |
| `/odom` | `nav_msgs/Odometry` | Published |
