# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_teleop
# Purpose: keyboard-controlled teleop — keyboard → /cmd_vel → mecanum kinematics → Arduino

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    robot_params = os.path.join(
        get_package_share_directory('guardian_bringup'), 'config', 'robot_params.yaml')

    return LaunchDescription([
        Node(
            package='guardian_teleop',
            executable='keyboard_teleop_node',
            name='keyboard_teleop_node',
            output='screen',
            prefix='xterm -e',
        ),
        Node(
            package='guardian_drive',
            executable='mecanum_kinematics_node',
            name='mecanum_kinematics_node',
            parameters=[robot_params],
        ),
        Node(
            package='guardian_drive',
            executable='serial_bridge_node',
            name='serial_bridge_node',
            parameters=[robot_params],
        ),
    ])
