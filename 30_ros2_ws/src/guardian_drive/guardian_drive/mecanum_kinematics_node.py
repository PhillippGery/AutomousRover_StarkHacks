# MIT License
# GUARDIAN — StarkHacks 2026
# Node: mecanum_kinematics_node
# Owner: Phillipp
# Purpose: converts /cmd_vel Twist to 4× wheel RPM targets using mecanum kinematics

from math import pi

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray


class MecanumKinematicsNode(Node):
    def __init__(self):
        super().__init__('mecanum_kinematics_node')

        self.declare_parameter('wheel_radius', 0.0748) # 6" VEXpro mecanum wheels need to find radius
        self.declare_parameter('wheel_base_length', 0.25)
        self.declare_parameter('wheel_base_width', 0.20)
        self.declare_parameter('max_rpm', 251.0)

        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.pub = self.create_publisher(Float32MultiArray, '/wheel_rpm', 10)

        self.get_logger().info('mecanum_kinematics_node started')

    def cmd_vel_callback(self, msg):
        r = self.get_parameter('wheel_radius').value
        l = self.get_parameter('wheel_base_length').value
        w = self.get_parameter('wheel_base_width').value
        max_rpm = self.get_parameter('max_rpm').value

        vx = msg.linear.x
        vy = msg.linear.y
        omega = msg.angular.z
        k = l / 2.0 + w / 2.0
        to_rpm = 60.0 / (2.0 * pi)

        fl = (vx - vy - k * omega) / r * to_rpm
        fr = (vx + vy + k * omega) / r * to_rpm
        bl = (vx + vy - k * omega) / r * to_rpm
        br = (vx - vy + k * omega) / r * to_rpm

        fl = max(-max_rpm, min(max_rpm, fl))
        fr = max(-max_rpm, min(max_rpm, fr))
        bl = max(-max_rpm, min(max_rpm, bl))
        br = max(-max_rpm, min(max_rpm, br))

        self.get_logger().debug(f'RPM FL={fl:.2f} FR={fr:.2f} BL={bl:.2f} BR={br:.2f}')

        out = Float32MultiArray()
        out.data = [fl, fr, bl, br]
        self.pub.publish(out)


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
