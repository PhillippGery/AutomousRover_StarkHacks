# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_full
# Owner: Phillipp
# Purpose: full autonomous mode — brings up all nodes

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
    # - arm_manager_node (guardian_arms)
    # - teleop_bridge_node (guardian_arms)
    # - quest_bridge_node (guardian_teleop)
    # - RViz2

    return LaunchDescription([
        # TODO: add Node() and IncludeLaunchDescription() calls here
    ])
