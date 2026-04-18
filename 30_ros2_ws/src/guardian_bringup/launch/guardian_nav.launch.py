# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_nav
# Purpose: navigation-only launch — drive chain + LIDAR + EKF + Nav2 + SLAM

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def launch_setup(context, *args, **kwargs):
    bringup_dir     = get_package_share_directory('guardian_bringup')
    description_dir = get_package_share_directory('guardian_description')
    nav2_dir        = get_package_share_directory('nav2_bringup')
    slam_dir        = get_package_share_directory('slam_toolbox')

    nav2_params  = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')
    ekf_params   = os.path.join(bringup_dir, 'config', 'ekf_params.yaml')
    robot_params = os.path.join(bringup_dir, 'config', 'robot_params.yaml')
    rviz_config  = os.path.join(bringup_dir, 'config', 'guardian.rviz')

    xacro_file  = os.path.join(description_dir, 'urdf', 'guardian.urdf.xacro')
    robot_desc  = xacro.process_file(xacro_file).toxml()

    sim_mode = LaunchConfiguration('sim_mode').perform(context).lower() == 'true'

    # ── Robot description (TF tree) ───────────────────────────────────────────
    nodes = [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            parameters=[{'robot_description': robot_desc}],
        ),

        # ── Drive chain ───────────────────────────────────────────────────────
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
            parameters=[robot_params, {'sim_mode': sim_mode}],
        ),

        # ── robot_localization EKF ────────────────────────────────────────────
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[ekf_params],
            remappings=[('odometry/filtered', '/odom_fused')],
        ),

        # ── RViz2 ─────────────────────────────────────────────────────────────
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        ),
    ]

    if not sim_mode:
        # ── Hardware-only nodes ───────────────────────────────────────────────
        nodes += [
            Node(
                package='realsense2_camera',
                executable='realsense2_camera_node',
                name='realsense2_camera',
                parameters=[{
                    'enable_pose': True,
                    'enable_fisheye1': False,
                    'enable_fisheye2': False,
                }],
            ),
            Node(
                package='l3xz_sweep_scanner',
                executable='l3xz_sweep_scanner_node',
                name='sweep_scanner',
                parameters=[{'serial_port': '/dev/ttyUSB0'}],
            ),
            Node(
                package='guardian_localization',
                executable='lidar_republisher_node',
                name='lidar_republisher_node',
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(slam_dir, 'launch', 'online_async_launch.py')
                ),
                launch_arguments={'params_file': nav2_params}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_dir, 'launch', 'navigation_launch.py')
                ),
                launch_arguments={
                    'params_file': nav2_params,
                    'use_sim_time': 'false',
                }.items(),
            ),
        ]

    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'sim_mode', default_value='false',
            description='Skip hardware nodes (lidar, realsense, serial) for bench testing'),
        OpaqueFunction(function=launch_setup),
    ])
