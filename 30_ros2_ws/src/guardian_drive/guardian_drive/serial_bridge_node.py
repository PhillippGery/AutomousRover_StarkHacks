# MIT License
# GUARDIAN — StarkHacks 2026
# Node: serial_bridge_node
# Purpose: sends RPM targets to Arduino over USB serial, reads encoder feedback, publishes /odom

import math
import serial
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')

        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('serial_baud', 115200)
        self.declare_parameter('wheel_radius', 0.048)
        self.declare_parameter('wheel_base_length', 0.25)
        self.declare_parameter('wheel_base_width', 0.20)

        port = self.get_parameter('serial_port').value
        baud = self.get_parameter('serial_baud').value
        self.ser = serial.Serial(port, baud, timeout=0.1)

        self.sub = self.create_subscription(
            Float32MultiArray, '/wheel_rpms', self.rpm_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.x = self.y = self.yaw = 0.0
        self.last_time = self.get_clock().now()

        self.create_timer(0.02, self.read_encoders)  # 50 Hz

        self.get_logger().info(f'serial_bridge_node started on {port}')

    def rpm_callback(self, msg: Float32MultiArray):
        fl, fr, bl, br = msg.data
        line = f'FL:{int(fl)} FR:{int(fr)} BL:{int(bl)} BR:{int(br)}\n'
        self.ser.write(line.encode())

    def read_encoders(self):
        if not self.ser.in_waiting:
            return
        try:
            line = self.ser.readline().decode().strip()
        except Exception:
            return

        # Expected: "ENC:FL:148 FR:151 BL:-149 BR:-152"
        if not line.startswith('ENC:'):
            return
        parts = {}
        for token in line[4:].split():
            k, _, v = token.partition(':')
            parts[k] = int(v)

        try:
            fl_rpm = parts['FL']; fr_rpm = parts['FR']
            bl_rpm = parts['BL']; br_rpm = parts['BR']
        except KeyError:
            return

        r = self.get_parameter('wheel_radius').value
        L = self.get_parameter('wheel_base_length').value / 2.0
        W = self.get_parameter('wheel_base_width').value / 2.0

        # RPM → rad/s
        k = 2.0 * math.pi / 60.0
        fl = fl_rpm * k; fr = fr_rpm * k
        bl = bl_rpm * k; br = br_rpm * k

        # Mecanum forward kinematics → body velocities
        vx    = r / 4.0 * (fl + fr + bl + br)
        vy    = r / 4.0 * (-fl + fr + bl - br)
        omega = r / (4.0 * (L + W)) * (-fl + fr - bl + br)

        now = self.get_clock().now()
        dt  = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        # Integrate pose
        self.x   += (vx * math.cos(self.yaw) - vy * math.sin(self.yaw)) * dt
        self.y   += (vx * math.sin(self.yaw) + vy * math.cos(self.yaw)) * dt
        self.yaw += omega * dt

        self._publish_odom(vx, vy, omega, now)

    def _publish_odom(self, vx, vy, omega, stamp):
        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        odom = Odometry()
        odom.header.stamp = stamp.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id  = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x  = vx
        odom.twist.twist.linear.y  = vy
        odom.twist.twist.angular.z = omega
        self.odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header.stamp    = stamp.to_msg()
        tf.header.frame_id = 'odom'
        tf.child_frame_id  = 'base_link'
        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.rotation.z = qz
        tf.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(tf)


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
