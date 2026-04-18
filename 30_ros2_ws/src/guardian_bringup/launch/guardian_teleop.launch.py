# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_teleop
# Purpose: keyboard-controlled teleop — keyboard → /cmd_vel → mecanum kinematics → Arduino

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='guardian_teleop',
            executable='keyboard_teleop_node',
            name='keyboard_teleop_node',
            output='screen',
        ),
        Node(
            package='guardian_drive',
            executable='mecanum_kinematics_node',
            name='mecanum_kinematics_node',
        ),
        Node(
            package='guardian_drive',
            executable='serial_bridge_node',
            name='serial_bridge_node',
        ),
    ])
