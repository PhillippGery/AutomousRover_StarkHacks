# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_teleop
# Owner: Victor
# Purpose: teleop-only fallback — joystick drive with mecanum kinematics and serial bridge

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[{
                'dev': '/dev/input/js0',
                'deadzone': 0.05,
            }],
        ),
        Node(
            package='guardian_teleop',
            executable='joystick_fallback_node',
            name='joystick_fallback_node',
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
