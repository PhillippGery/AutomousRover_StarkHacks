# guardian_bringup

**Owner: Phillipp**

Launch files, EKF parameters, Nav2 parameters, and robot configuration for GUARDIAN.

## Launch Files

| File | Purpose |
|------|---------|
| `guardian_full.launch.py` | Full autonomous mode — all nodes |
| `guardian_nav.launch.py` | Navigation only — no arms, no Quest |
| `guardian_teleop.launch.py` | Teleop fallback — joystick + Quest bridge |

## Config Files

| File | Purpose |
|------|---------|
| `ekf_params.yaml` | robot_localization EKF configuration |
| `nav2_params.yaml` | Nav2 navigation stack parameters |
| `robot_params.yaml` | Robot geometry, serial port, hardware params |
