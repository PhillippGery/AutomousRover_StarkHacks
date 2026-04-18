# MIT License
# GUARDIAN — StarkHacks 2026
# Node: mecanum_kinematics_node
# Purpose: converts /cmd_vel Twist to 4× wheel RPM targets using mecanum kinematics

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray


class MecanumKinematicsNode(Node):
    def __init__(self):
        super().__init__('mecanum_kinematics_node')

        self.declare_parameter('wheel_radius', 0.048)       # metres
        self.declare_parameter('wheel_base_length', 0.25)   # front-to-back (metres)
        self.declare_parameter('wheel_base_width', 0.20)    # left-to-right (metres)
        self.declare_parameter('max_rpm', 300.0)

        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.pub = self.create_publisher(Float32MultiArray, '/wheel_rpms', 10)

        self.get_logger().info('mecanum_kinematics_node started')

    def cmd_vel_callback(self, msg: Twist):
        r  = self.get_parameter('wheel_radius').value
        L  = self.get_parameter('wheel_base_length').value / 2.0
        W  = self.get_parameter('wheel_base_width').value / 2.0
        max_rpm = self.get_parameter('max_rpm').value

        vx    = msg.linear.x
        vy    = msg.linear.y
        omega = msg.angular.z

        # Mecanum inverse kinematics (rad/s per wheel)
        fl = (vx - vy - (L + W) * omega) / r
        fr = (vx + vy + (L + W) * omega) / r
        bl = (vx + vy - (L + W) * omega) / r
        br = (vx - vy + (L + W) * omega) / r

        # rad/s → RPM
        k = 60.0 / (2.0 * math.pi)
        fl_rpm, fr_rpm, bl_rpm, br_rpm = fl * k, fr * k, bl * k, br * k

        # Clamp to max RPM while preserving ratios
        peak = max(abs(fl_rpm), abs(fr_rpm), abs(bl_rpm), abs(br_rpm), 1e-6)
        if peak > max_rpm:
            scale = max_rpm / peak
            fl_rpm *= scale; fr_rpm *= scale
            bl_rpm *= scale; br_rpm *= scale

        out = Float32MultiArray()
        out.data = [fl_rpm, fr_rpm, bl_rpm, br_rpm]
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
