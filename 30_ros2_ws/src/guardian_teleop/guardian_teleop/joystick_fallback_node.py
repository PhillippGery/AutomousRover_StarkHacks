# MIT License
# GUARDIAN — StarkHacks 2026
# Node: joystick_fallback_node
# Owner: Victor
# Purpose: maps Qualcomm joystick /joy input to /cmd_vel for manual rover drive

import rclpy
from rclpy.node import Node
# TODO: import message types needed
# from sensor_msgs.msg import Joy
# from geometry_msgs.msg import Twist


class JoystickFallbackNode(Node):
    def __init__(self):
        super().__init__('joystick_fallback_node')
        self.get_logger().info('joystick_fallback_node started')

        # TODO: declare parameters
        # self.declare_parameter('linear_scale', 0.5)   # m/s max
        # self.declare_parameter('angular_scale', 1.0)  # rad/s max
        # self.declare_parameter('strafe_scale', 0.5)   # m/s max lateral

        # TODO: create subscribers
        # self.sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)

        # TODO: create publishers
        # self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    # TODO: implement callbacks
    # def joy_callback(self, msg):
    #     twist = Twist()
    #     # Map axes: axes[1]=forward, axes[0]=strafe, axes[3]=rotate
    #     # twist.linear.x = msg.axes[1] * self.get_parameter('linear_scale').value
    #     # twist.linear.y = msg.axes[0] * self.get_parameter('strafe_scale').value
    #     # twist.angular.z = msg.axes[3] * self.get_parameter('angular_scale').value
    #     # self.pub.publish(twist)
    #     pass


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
