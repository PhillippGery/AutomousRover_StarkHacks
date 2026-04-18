import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('guardian_bringup')
    description_dir = get_package_share_directory('guardian_description')
    slam_dir = get_package_share_directory('slam_toolbox')

    robot_params = os.path.join(bringup_dir, 'config', 'robot_params.yaml')
    nav2_params = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(bringup_dir, 'config', 'guardian_mapping.rviz')

    robot_desc = xacro.process_file(
        os.path.join(description_dir, 'urdf', 'guardian.urdf.xacro')
    ).toxml()

    lidar_port = LaunchConfiguration('lidar_port')
    enable_slam = LaunchConfiguration('enable_slam')
    enable_rviz = LaunchConfiguration('enable_rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'lidar_port',
            default_value='/dev/ttyUSB0',
            description='Serial port for the Scanse Sweep lidar',
        ),
        DeclareLaunchArgument(
            'enable_slam',
            default_value='false',
            description='Start SLAM Toolbox after the lidar and /odom are stable',
        ),
        DeclareLaunchArgument(
            'enable_rviz',
            default_value='true',
            description='Start RViz with the hardware bringup view',
        ),

        # Publish the robot TF tree, including the fixed laser mount.
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

        # Drive chain: /cmd_vel -> /wheel_rpm -> serial motor controller + /odom
        Node(
            package='guardian_drive',
            executable='mecanum_kinematics_node',
            name='mecanum_kinematics_node',
            parameters=[robot_params],
            output='screen',
        ),
        Node(
            package='guardian_drive',
            executable='guardian_drive_node',
            name='guardian_drive',
            parameters=[robot_params, {'publish_odom': True}],
            output='screen',
        ),

        # Reset the lidar before the driver attaches so stale scan state does not
        # block the real hardware startup sequence.
        ExecuteProcess(
            cmd=[
                'bash',
                '-c',
                ['stty -F ', lidar_port, ' 115200 && '
                 'printf "DX\n" > ', lidar_port, ' && sleep 1 && '
                 'printf "RR\n" > ', lidar_port],
            ],
            output='screen',
        ),
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='l3xz_sweep_scanner',
                    executable='l3xz_sweep_scanner_node',
                    name='sweep_scanner',
                    parameters=[{
                        'serial_port': lidar_port,
                        'topic': '/sweep/scan',
                        'frame_id': 'laser',
                        'rotation_speed': 10,
                        'sample_rate': 1000,
                    }],
                    output='screen',
                ),
            ],
        ),
        Node(
            package='guardian_localization',
            executable='lidar_republisher_node',
            name='lidar_republisher_node',
            parameters=[{
                'input_topic': '/sweep/scan',
                'output_topic': '/scan',
                'frame_id': 'laser',
                'timestamp_offset_sec': 0.05,
            }],
            output='screen',
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
            condition=IfCondition(enable_rviz),
        ),

        # Leave SLAM opt-in until the odometry chain is reliable enough to
        # support scan matching.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_dir, 'launch', 'online_async_launch.py')
            ),
            launch_arguments={
                'slam_params_file': nav2_params,
                'use_sim_time': 'false',
            }.items(),
            condition=IfCondition(enable_slam),
        ),
    ])
