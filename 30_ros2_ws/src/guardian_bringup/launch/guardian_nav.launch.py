# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_nav
# Owner: Phillipp
# Purpose: navigation-only launch — no arms, no Quest bridge

from launch import LaunchDescription


def generate_launch_description():
    # TODO: launch nodes:
    # - mecanum_kinematics_node (guardian_drive)
    # - serial_bridge_node (guardian_drive)
    # - Intel RealSense T265 (realsense2_camera)
    # - Scanse Sweep LIDAR (l3xz_sweep_scanner)
    # - lidar_republisher_node (guardian_localization)
    # - robot_localization EKF (ekf_params.yaml)
    # - Nav2 bringup (nav2_params.yaml)
    # - RViz2

    return LaunchDescription([
        # TODO: add Node() and IncludeLaunchDescription() calls here
    ])
