# Quest Bridge

**Owner: Victor**

WebSocket server that receives Meta Quest 3 head tracking and hand data and forwards it to ROS2 topics.

## Usage

```bash
pip install websockets
python websocket_bridge.py --host 0.0.0.0 --port 8765
```

The Quest companion app should connect to `ws://<minipc-ip>:8765`.

## Data Format

TODO: define JSON message format from Quest app at hackathon.

Expected fields:
- `head_pose`: 7-DOF pose (x, y, z, qx, qy, qz, qw)
- `left_hand`: array of joint poses
- `right_hand`: array of joint poses
- `timestamp`: Unix timestamp in seconds
