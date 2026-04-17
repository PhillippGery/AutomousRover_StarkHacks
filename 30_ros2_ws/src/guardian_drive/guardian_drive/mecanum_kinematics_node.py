# MIT License
# GUARDIAN — StarkHacks 2026
# Node: mecanum_kinematics_node
# Owner: Phillipp
# Purpose: converts /cmd_vel Twist to 4× wheel RPM targets using mecanum kinematics

import rclpy
from rclpy.node import Node
# TODO: import message types needed
# from geometry_msgs.msg import Twist
# from std_msgs.msg import Float32MultiArray


class MecanumKinematicsNode(Node):
    def __init__(self):
        super().__init__('mecanum_kinematics_node')
        self.get_logger().info('mecanum_kinematics_node started')

        # TODO: declare parameters
        # self.declare_parameter('wheel_radius', 0.048)
        # self.declare_parameter('wheel_base_length', 0.25)
        # self.declare_parameter('wheel_base_width', 0.20)
        # self.declare_parameter('max_rpm', 300.0)

        # TODO: create subscribers
        # self.sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        # TODO: create publishers
        # self.pub = self.create_publisher(Float32MultiArray, '/wheel_rpms', 10)

    # TODO: implement callbacks
    # def cmd_vel_callback(self, msg):
    #     vx = msg.linear.x
    #     vy = msg.linear.y
    #     omega = msg.angular.z
    #
    #     r = self.get_parameter('wheel_radius').value
    #     L = self.get_parameter('wheel_base_length').value / 2.0
    #     W = self.get_parameter('wheel_base_width').value / 2.0
    #
    #     # Mecanum kinematics
    #     fl = (vx - vy - (L + W) * omega) / r
    #     fr = (vx + vy + (L + W) * omega) / r
    #     bl = (vx + vy - (L + W) * omega) / r
    #     br = (vx - vy + (L + W) * omega) / r
    #
    #     # Convert rad/s to RPM
    #     fl_rpm = fl * 60.0 / (2.0 * 3.14159)
    #     fr_rpm = fr * 60.0 / (2.0 * 3.14159)
    #     bl_rpm = bl * 60.0 / (2.0 * 3.14159)
    #     br_rpm = br * 60.0 / (2.0 * 3.14159)
    #
    #     out = Float32MultiArray()
    #     out.data = [fl_rpm, fr_rpm, bl_rpm, br_rpm]
    #     self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = MecanumKinematicsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
