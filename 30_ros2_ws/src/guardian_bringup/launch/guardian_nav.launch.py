# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_nav
# Purpose: navigation-only launch — drive chain + LIDAR + EKF + Nav2 + SLAM

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir  = get_package_share_directory('guardian_bringup')
    nav2_dir     = get_package_share_directory('nav2_bringup')
    slam_dir     = get_package_share_directory('slam_toolbox')

    nav2_params  = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')
    ekf_params   = os.path.join(bringup_dir, 'config', 'ekf_params.yaml')
    robot_params = os.path.join(bringup_dir, 'config', 'robot_params.yaml')

    # ── Drive chain ───────────────────────────────────────────────────────────
    mecanum_node = Node(
        package='guardian_drive',
        executable='mecanum_kinematics_node',
        name='mecanum_kinematics_node',
        parameters=[robot_params],
    )

    serial_node = Node(
        package='guardian_drive',
        executable='serial_bridge_node',
        name='serial_bridge_node',
        parameters=[robot_params],
    )

    # ── Intel RealSense T265 (visual-inertial odometry) ───────────────────────
    realsense_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='realsense2_camera',
        parameters=[{
            'enable_pose': True,
            'enable_fisheye1': False,
            'enable_fisheye2': False,
        }],
    )

    # ── Scanse Sweep LIDAR ────────────────────────────────────────────────────
    sweep_node = Node(
        package='l3xz_sweep_scanner',
        executable='l3xz_sweep_scanner_node',
        name='sweep_scanner',
        parameters=[{'serial_port': '/dev/ttyUSB0'}],
    )

    lidar_republisher_node = Node(
        package='guardian_localization',
        executable='lidar_republisher_node',
        name='lidar_republisher_node',
    )

    # ── robot_localization EKF (wheel odom + T265 + IMU fusion) ──────────────
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        parameters=[ekf_params],
        remappings=[('odometry/filtered', '/odom_fused')],
    )

    # ── SLAM Toolbox (online mapping) ─────────────────────────────────────────
    slam_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_dir, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={'params_file': nav2_params}.items(),
    )

    # ── Nav2 ──────────────────────────────────────────────────────────────────
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': nav2_params,
            'use_sim_time': 'false',
        }.items(),
    )

    # ── RViz2 ─────────────────────────────────────────────────────────────────
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[],
    )

    return LaunchDescription([
        mecanum_node,
        serial_node,
        realsense_node,
        sweep_node,
        lidar_republisher_node,
        ekf_node,
        slam_node,
        nav2,
        rviz_node,
    ])
