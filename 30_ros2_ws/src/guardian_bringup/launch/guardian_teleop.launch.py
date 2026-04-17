# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_teleop
# Owner: Victor
# Purpose: teleop-only fallback — joystick and Quest bridge without autonomous nav

from launch import LaunchDescription


def generate_launch_description():
    # TODO: launch nodes:
    # - mecanum_kinematics_node (guardian_drive)
    # - serial_bridge_node (guardian_drive)
    # - joystick_fallback_node (guardian_teleop)
    # - quest_bridge_node (guardian_teleop)
    # - teleop_bridge_node (guardian_arms) — optional

    return LaunchDescription([
        # TODO: add Node() calls here
    ])
