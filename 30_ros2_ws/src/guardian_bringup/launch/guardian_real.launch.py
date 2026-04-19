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
    rviz_config = os.path.join(bringup_dir, 'config', 'guardian_nav.rviz')
    robot_desc = xacro.process_file(
        os.path.join(description_dir, 'urdf', 'guardian.urdf.xacro')).toxml()

    return LaunchDescription([

        # ── 1. Robot state ───────────────────────────────────────────
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': False}],
            output='screen',
        ),

        # ── 2. Intel RealSense T265 (The Localization Source) ───────────
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='realsense2_camera',
            parameters=[{
                'camera_name': 'camera',
                'use_sim_time': False,
                'enable_pose': True,
                # Force TF publication
                'publish_tf': True,
                'publish_odom_tf': True,
                'tf_publish_rate': 30.0,
                # Explicitly name the frames
                'odom_frame_id': 'odom', 
                'pose_frame_id': 'base_link',
                'base_frame_id': 'base_link',
            }],
            output='screen',
        ),
        
        # Bridge the T265 'odom_frame' to the global 'odom'
        # Node(
        #     package='tf2_ros',
        #     executable='static_transform_publisher',
        #     name='odom_to_t265_odom',
        #     arguments=['0', '0', '0', '0', '0', '0', 'odom', 'odom_frame'],
        # ),

        # ── 3. Scanse Sweep LIDAR ──────────────────────────────────────────────
        Node(
            package='l3xz_sweep_scanner',
            executable='l3xz_sweep_scanner_node',
            name='sweep_scanner',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'frame_id': 'laser',
            }],
            output='screen',
        ),

        # ── 4. SLAM Toolbox ─────────────────────────────────────────────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_dir, 'launch', 'online_async_launch.py')
            ),
            launch_arguments={'use_sim_time': 'false'}.items(),
        ),

        # ── 5. Nav2 core nodes ──────────────────────────────────────────────────
        TimerAction(period=5.0, actions=[
            Node(package='nav2_controller', executable='controller_server', name='controller_server', parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_planner', executable='planner_server', name='planner_server', parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_behaviors', executable='behavior_server', name='behavior_server', parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator', parameters=[nav2_params, {'use_sim_time': False}]),
            Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_navigation', 
                 parameters=[{'use_sim_time': False, 'autostart': True, 'node_names': ['controller_server', 'planner_server', 'behavior_server', 'bt_navigator']}]),
        ]),
    ])