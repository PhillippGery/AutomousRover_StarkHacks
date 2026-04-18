<a href="https://107-systems.org/"><img align="right" src="https://raw.githubusercontent.com/107-systems/.github/main/logo/107-systems.png" width="15%"></a>
:floppy_disk: `l3xz_sweep_scanner`
==================================
[![Build Status](https://github.com/107-systems/l3xz_sweep_scanner/actions/workflows/ros2.yml/badge.svg)](https://github.com/107-systems/l3xz_sweep_scanner/actions/workflows/ros2.yml)
[![Spell Check status](https://github.com/107-systems/l3xz_sweep_scanner/actions/workflows/spell-check.yml/badge.svg)](https://github.com/107-systems/l3xz_sweep_scanner/actions/workflows/spell-check.yml)

ROS driver for Scanse Sweep 360° 2D LIDAR.

<p align="center">
  <a href="https://github.com/107-systems/l3xz"><img src="https://raw.githubusercontent.com/107-systems/.github/main/logo/l3xz-logo-memento-mori-github.png" width="40%"></a>
</p>

### How-to-build
```bash
cd $COLCON_WS/src
git clone https://github.com/107-systems/l3xz_sweep_scanner
cd $COLCON_WS
source /opt/ros/humble/setup.bash
colcon build --packages-select l3xz_sweep_scanner
```

### How-to-run
```bash
cd $COLCON_WS
. install/setup.bash
ros2 launch l3xz_sweep_scanner laser.py
rviz2 --display-config src/l3xz_sweep_scanner/rviz/laser.rviz
```
**Note**: Possible you need to configure the right USB port in `launch`/[`laser.py`](launch/laser.py).

<p align="center">
  <img src="doc/img/laser-scan-rviz.png" width="40%">
</p>

### Interface Documentation
#### Published Topics
| Default Name | Type |
|:-:|:-:|
| `/l3xz/laser` | [`sensor_msgs/LaserScan`](https://docs.ros.org/en/noetic/api/sensor_msgs/html/msg/LaserScan.html) |

#### Parameters
| Name | Default | Description |
|:-:|:-:|-|
| `topic` | `laser ` | Name of ROS2 topic under which the `sensor_msgs/LaserScan` data is streamed. |
| `serial_port` | `/dev/ttyUSB0 ` | Serial port under which the Scanse Sweep is connected to the system. |
| `rotation_speed` | 1-10 | Rotations per second of the sensor head. |
| `sample_rate ` | 500, 750, 1000 | Laser scan rate in Hz, i.e. 500 = 500 laser distance measurements per second. |
| `frame_id` | `laser_frame` | Topic under which the is published. |
