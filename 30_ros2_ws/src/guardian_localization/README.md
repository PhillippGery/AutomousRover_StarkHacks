# guardian_localization

**Owner: Phillipp**

LIDAR republisher and sensor preprocessing to feed Nav2 and the EKF.

## Nodes

| Node | Purpose |
|------|---------|
| `lidar_republisher_node` | Republishes Scanse Sweep scan data to `/scan` topic for Nav2 |

## Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/sweep/scan` | `sensor_msgs/LaserScan` | Subscribed (from l3xz_sweep_scanner) |
| `/scan` | `sensor_msgs/LaserScan` | Published (to Nav2 costmaps) |
