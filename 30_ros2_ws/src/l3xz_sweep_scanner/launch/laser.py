from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
  return LaunchDescription([
    Node(
      package='l3xz_sweep_scanner',
      executable='l3xz_sweep_scanner_node',
      name='sweep_node',
      namespace='l3xz',
      output='screen',
      parameters=[
          {'topic' : 'laser'},
          {'serial_port' : '/dev/serial/by-id/usb-FTDI_FT230X_Basic_UART_DO008MI4-if00-port0'},
          {'rotation_speed': 5},
          {'sample_rate': 750},
          {'frame_id' : 'laser_link'}
      ]
    ),
    Node(package = "tf2_ros",
         executable = "static_transform_publisher",
         name="base_link_to_laser_link",
         namespace='l3xz',
         output='screen',
         arguments = ["0.06", "0", "0.8", "0", "0", "0", "base_link", "laser_link"]
    )
  ])
