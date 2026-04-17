# guardian_teleop

**Owner: Victor**

Meta Quest 3 mixed reality teleoperation and joystick fallback for GUARDIAN.

## Nodes

| Node | Purpose |
|------|---------|
| `quest_bridge_node` | Receives Quest head tracking and hand data via WebSocket, publishes to ROS2 topics |
| `joystick_fallback_node` | Maps joystick `/joy` input to `/cmd_vel` for manual rover drive |

## Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/quest/head_pose` | `geometry_msgs/PoseStamped` | Published |
| `/quest/hand_poses` | `geometry_msgs/PoseArray` | Published |
| `/joy` | `sensor_msgs/Joy` | Subscribed |
| `/cmd_vel` | `geometry_msgs/Twist` | Published |

## WebSocket Bridge

The Quest 3 sends data via WebSocket from the companion app running on-headset. See [50_teleop/quest_bridge/](../../../50_teleop/quest_bridge/) for the bridge server.
