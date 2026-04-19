import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('guardian_bringup')
    description_dir = get_package_share_directory('guardian_description')
    nav2_dir = get_package_share_directory('nav2_bringup')
    slam_dir = get_package_share_directory('slam_toolbox')

    nav2_params = os.path.join(bringup_dir, 'config', 'nav2_params_real.yaml')
    ekf_params = os.path.join(bringup_dir, 'config', 'ekf_params_real.yaml')
    rviz_config = os.path.join(bringup_dir, 'config', 'guardian_real.rviz')
    robot_desc = xacro.process_file(
        os.path.join(description_dir, 'urdf', 'guardian.urdf.xacro')).toxml()
    use_dummy_odom = LaunchConfiguration('use_dummy_odom')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_dummy_odom',
            default_value='false',
            description='Publish debug /odom from /cmd_vel instead of using Arduino encoder odometry',
        ),
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
        ExecuteProcess(
            cmd=['bash', '-c',
                 'stty -F /dev/ttyUSB0 115200 && '
                 'printf "DX\n" > /dev/ttyUSB0 && sleep 1 && '
                 'printf "RR\n" > /dev/ttyUSB0'],
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
                        'serial_port': '/dev/ttyUSB0',
                        'topic': '/sweep/scan',
                        'frame_id': 'laser',
                        'rotation_speed': 5,
                        'sample_rate': 500,
                    }],
                    output='screen',
                ),
            ],
        ),
        Node(
            package='guardian_drive',
            executable='serial_bridge_node',
            name='serial_bridge_node',
            condition=UnlessCondition(use_dummy_odom),
            parameters=[{
                'serial_port': '/dev/ttyUSB1',
                'baud_rate': 115200,
                'sim_mode': False,
                'publish_odom': True,
                'publish_tf': False,
            }],
            output='screen',
        ),
        Node(
            package='guardian_bringup',
            executable='dummy_odom_node',
            name='dummy_odom_node',
            condition=IfCondition(use_dummy_odom),
            output='screen',
        ),
        Node(
            package='guardian_drive',
            executable='mecanum_kinematics_node',
            name='mecanum_kinematics_node',
            parameters=[{'use_sim_time': False}],
            output='screen',
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[ekf_params, {'use_sim_time': False}],
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': False}],
            output='screen',
        ),
        TimerAction(
            period=15.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(slam_dir, 'launch', 'online_async_launch.py')
                    ),
                    launch_arguments={
                        'slam_params_file': nav2_params,
                        'use_sim_time': 'false',
                    }.items(),
                ),
            ],
        ),
        TimerAction(
            period=18.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(nav2_dir, 'launch', 'navigation_launch.py')
                    ),
                    launch_arguments={
                        'params_file': nav2_params,
                        'use_sim_time': 'false',
                    }.items(),
                ),
            ],
        ),
        Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            name='teleop',
            output='screen',
            prefix='xterm -e',
        ),
    ])
