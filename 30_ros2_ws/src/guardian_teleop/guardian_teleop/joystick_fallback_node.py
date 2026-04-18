# MIT License
# GUARDIAN — StarkHacks 2026
# Node: joystick_fallback_node
# Owner: Victor
# Purpose: maps Qualcomm joystick /joy input to /cmd_vel for manual rover drive

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoystickFallbackNode(Node):
    def __init__(self):
        super().__init__('joystick_fallback_node')

        self.declare_parameter('linear_x_axis', 1)
        self.declare_parameter('linear_y_axis', 0)
        self.declare_parameter('angular_axis', 3)
        self.declare_parameter('deadman_button', 5)
        self.declare_parameter('linear_x_scale', 0.5)
        self.declare_parameter('linear_y_scale', 0.5)
        self.declare_parameter('angular_scale', 1.0)

        self.sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info('joystick_fallback_node started')

    def joy_callback(self, msg):
        deadman_btn = self.get_parameter('deadman_button').value
        twist = Twist()

        if len(msg.buttons) <= deadman_btn or not msg.buttons[deadman_btn]:
            self.pub.publish(twist)
            return

        lx_axis = self.get_parameter('linear_x_axis').value
        ly_axis = self.get_parameter('linear_y_axis').value
        ang_axis = self.get_parameter('angular_axis').value
        lx_scale = self.get_parameter('linear_x_scale').value
        ly_scale = self.get_parameter('linear_y_scale').value
        ang_scale = self.get_parameter('angular_scale').value

        if len(msg.axes) > lx_axis:
            twist.linear.x = msg.axes[lx_axis] * lx_scale
        if len(msg.axes) > ly_axis:
            twist.linear.y = msg.axes[ly_axis] * ly_scale
        if len(msg.axes) > ang_axis:
            twist.angular.z = msg.axes[ang_axis] * ang_scale

        self.get_logger().debug(
            f'CMD: vx={twist.linear.x:.3f} vy={twist.linear.y:.3f} omega={twist.angular.z:.3f}'
        )
        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = JoystickFallbackNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
