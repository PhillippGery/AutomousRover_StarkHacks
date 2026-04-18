# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_full
# Purpose: full autonomous mode — nav stack + arms + Quest bridge

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    bringup_dir = get_package_share_directory('guardian_bringup')

    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'guardian_nav.launch.py')
        ),
    )

    # TODO (arms team): add arm_manager_node, teleop_bridge_node
    # TODO (teleop team): add quest_bridge_node

    return LaunchDescription([
        nav_launch,
    ])
