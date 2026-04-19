# guardian_drive

**Owner: Phillipp**

Mecanum wheel kinematics and Arduino serial bridge.

## Nodes

| Node | Purpose |
|------|---------|
| `mecanum_kinematics_node` | Converts `/cmd_vel` Twist → 4× wheel RPM targets |
| `serial_bridge_node` | Sends RPM targets to the motor controller, interprets wheel telemetry, and publishes `/odom` |

## Serial modes

| Mode | Commands sent | Telemetry read | Interpretation |
|------|---------------|----------------|----------------|
| `dual_esp32` | `M1:<rpm> M2:<rpm>` per board | `ENC:M1:<ticks> M2:<ticks>` | Cumulative ticks per wheel pair |
| `single_arduino_flfrblbr_ticks` | `FL:<rpm> FR:<rpm> BL:<rpm> BR:<rpm>` | `ENC:FL:<ticks> FR:<ticks> BL:<ticks> BR:<ticks>` | Cumulative ticks for all four wheels |
| `single_arduino_m1234_velocity` | `M1:<rpm> M2:<rpm> M3:<rpm> M4:<rpm>` | `ENC:M1:<ticks_per_sec> M2:<ticks_per_sec> M3:<ticks_per_sec> M4:<ticks_per_sec>` | Direct wheel velocity in ticks/sec |

## Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/cmd_vel` | `geometry_msgs/Twist` | Subscribed |
| `/wheel_rpms` | `std_msgs/Float32MultiArray` | Published (FL, FR, BL, BR) |
| `/odom` | `nav_msgs/Odometry` | Published |
