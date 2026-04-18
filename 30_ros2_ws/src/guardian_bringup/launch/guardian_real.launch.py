# MIT License
# GUARDIAN — StarkHacks 2026
# Launch: guardian_real
# Purpose: real-hardware autonomous bringup with T265 odometry + Sweep LIDAR + Nav2

import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('guardian_bringup')
    description_dir = get_package_share_directory('guardian_description')
    slam_dir = get_package_share_directory('slam_toolbox')

    nav2_params = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')
    robot_params = os.path.join(bringup_dir, 'config', 'robot_params.yaml')
    rviz_config = os.path.join(bringup_dir, 'config', 'guardian_nav.rviz')
    robot_desc = xacro.process_file(
        os.path.join(description_dir, 'urdf', 'guardian.urdf.xacro')).toxml()

    return LaunchDescription([

        # ── 1. Robot state / TF tree ───────────────────────────────────────────
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': False}],
            output='screen',
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': False}],
            output='screen',
        ),

        # ── 2. Drive chain ─────────────────────────────────────────────────────
        Node(
            package='guardian_drive',
            executable='mecanum_kinematics_node',
            name='mecanum_kinematics_node',
            parameters=[robot_params],
            output='screen',
        ),
        Node(
            package='guardian_drive',
            executable='serial_bridge_node',
            name='serial_bridge_node',
            parameters=[robot_params, {
                'sim_mode': False,
                'publish_odom': False,
            }],
            output='screen',
        ),

        # ── 3. Intel RealSense T265 ─────────────────────────────────────────────
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='realsense2_camera',
            parameters=[{
                'camera_name': 'camera',
                'use_sim_time': False,
                'enable_pose': True,
                'enable_fisheye1': False,
                'enable_fisheye2': False,
                'wait_for_device_timeout': 10.0,
                'publish_tf': True,
                'publish_odom_tf': True,
                'tf_publish_rate': 30.0,
                'base_frame_id': 'link',
                'odom_frame_id': 'odom_frame',
            }],
            remappings=[
                ('/camera/odom/sample', '/odom'),
            ],
            output='screen',
        ),

        # The current realsense-ros build publishes odom TF as odom_frame ->
        # camera_pose_frame, so bridge that into Nav2's expected odom -> base_link.
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='odom_to_t265_odom',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'odom_frame'],
            parameters=[{'use_sim_time': False}],
            output='screen',
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='t265_pose_to_base_link',
            arguments=['0', '0', '0', '0', '0', '0', 'camera_pose_frame', 'base_link'],
            parameters=[{'use_sim_time': False}],
            output='screen',
        ),

        # ── 4. Scanse Sweep LIDAR ──────────────────────────────────────────────
        ExecuteProcess(
            cmd=['bash', '-c',
                 'stty -F /dev/ttyUSB0 115200 && '
                 'printf "DX\n" > /dev/ttyUSB0 && sleep 1 && '
                 'printf "RR\n" > /dev/ttyUSB0'],
            output='screen',
        ),
        TimerAction(period=4.0, actions=[
            Node(
                package='l3xz_sweep_scanner',
                executable='l3xz_sweep_scanner_node',
                name='sweep_scanner',
                parameters=[{
                    'serial_port': '/dev/ttyUSB0',
                    'topic': '/sweep/scan',
                    'frame_id': 'laser',
                    'rotation_speed': 10,
                    'sample_rate': 1000,
                }],
                output='screen',
            ),
        ]),
        Node(
            package='guardian_localization',
            executable='lidar_republisher_node',
            name='lidar_republisher_node',
            parameters=[{
                'input_topic': '/sweep/scan',
                'output_topic': '/scan',
                'frame_id': 'laser',
            }],
            output='screen',
        ),

        # ── 5. SLAM Toolbox ─────────────────────────────────────────────────────
        TimerAction(period=5.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(slam_dir, 'launch', 'online_async_launch.py')
                ),
                launch_arguments={
                    'slam_params_file': nav2_params,
                    'use_sim_time': 'false',
                }.items(),
            ),
        ]),

        # ── 6. Nav2 core nodes ──────────────────────────────────────────────────
        # Delay Nav2 until the T265 and TF bridge chain are already present.
        TimerAction(period=15.0, actions=[
            Node(package='nav2_controller', executable='controller_server',
                 name='controller_server', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}],
                 remappings=[('cmd_vel', 'cmd_vel_nav')]),
            Node(package='nav2_smoother', executable='smoother_server',
                 name='smoother_server', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_planner', executable='planner_server',
                 name='planner_server', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_behaviors', executable='behavior_server',
                 name='behavior_server', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_bt_navigator', executable='bt_navigator',
                 name='bt_navigator', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_waypoint_follower', executable='waypoint_follower',
                 name='waypoint_follower', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_velocity_smoother', executable='velocity_smoother',
                 name='velocity_smoother', output='screen',
                 parameters=[nav2_params, {'use_sim_time': False}],
                 remappings=[('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', 'cmd_vel')]),
            Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
                 name='lifecycle_manager_navigation', output='screen',
                 parameters=[{'use_sim_time': False,
                               'autostart': True,
                               'bond_timeout': 0.0,
                               'node_names': [
                                   'controller_server', 'smoother_server',
                                   'planner_server', 'behavior_server',
                                   'bt_navigator', 'waypoint_follower',
                                   'velocity_smoother']}]),
        ]),

        # ── 7. RViz2 ────────────────────────────────────────────────────────────
        TimerAction(period=15.0, actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': False}],
                output='screen',
            ),
        ]),

    ])
