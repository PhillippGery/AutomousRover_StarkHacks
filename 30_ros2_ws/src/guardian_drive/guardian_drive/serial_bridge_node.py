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

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('serial_timeout', 1.0)
        self.declare_parameter('wheel_radius', 0.0748)
        self.declare_parameter('wheel_base_length', 0.25)
        self.declare_parameter('wheel_base_width', 0.20)

        port    = self.get_parameter('serial_port').value
        baud    = self.get_parameter('baud_rate').value
        timeout = self.get_parameter('serial_timeout').value

        try:
            self.ser = serial.Serial(port, baud, timeout=timeout)
            self.get_logger().info(f'Opened serial port {port} at {baud} baud')
        except serial.SerialException as e:
            self.get_logger().warn(f'Could not open serial port {port}: {e}')
            self.ser = None

        self.sub = self.create_subscription(
            Float32MultiArray, '/wheel_rpm', self.rpm_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.x = self.y = self.yaw = 0.0
        self.last_time = self.get_clock().now()

        self.create_timer(0.02, self.read_encoders)  # 50 Hz

        self.get_logger().info('serial_bridge_node started')

    def rpm_callback(self, msg: Float32MultiArray):
        if self.ser is None:
            return
        if len(msg.data) < 4:
            self.get_logger().warn('wheel_rpm message has fewer than 4 values')
            return
        fl, fr, bl, br = (int(round(v)) for v in msg.data[:4])
        line = f'FL:{fl} FR:{fr} BL:{bl} BR:{br}\n'
        try:
            self.ser.write(line.encode())
        except serial.SerialException as e:
            self.get_logger().error(f'Serial write error: {e}')

    def read_encoders(self):
        if self.ser is None or not self.ser.in_waiting:
            return
        try:
            raw = self.ser.readline()
        except serial.SerialException as e:
            self.get_logger().error(f'Serial read error: {e}')
            return

        line = raw.decode(errors='replace').strip()
        if not line.startswith('ENC:'):
            return

        try:
            parts = {}
            for token in line[4:].split():
                k, _, v = token.partition(':')
                parts[k] = int(v)
            fl_rpm = parts['FL']; fr_rpm = parts['FR']
            bl_rpm = parts['BL']; br_rpm = parts['BR']
        except Exception as e:
            self.get_logger().warn(f'Failed to parse encoder line "{line}": {e}')
            return

        self.get_logger().debug(
            f'Encoders FL={fl_rpm} FR={fr_rpm} BL={bl_rpm} BR={br_rpm}')

        r = self.get_parameter('wheel_radius').value
        L = self.get_parameter('wheel_base_length').value / 2.0
        W = self.get_parameter('wheel_base_width').value / 2.0

        k = 2.0 * math.pi / 60.0
        fl = fl_rpm * k; fr = fr_rpm * k
        bl = bl_rpm * k; br = br_rpm * k

        vx    = r / 4.0 * (fl + fr + bl + br)
        vy    = r / 4.0 * (-fl + fr + bl - br)
        omega = r / (4.0 * (L + W)) * (-fl + fr - bl + br)

        now = self.get_clock().now()
        dt  = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        self.x   += (vx * math.cos(self.yaw) - vy * math.sin(self.yaw)) * dt
        self.y   += (vx * math.sin(self.yaw) + vy * math.cos(self.yaw)) * dt
        self.yaw += omega * dt

        self._publish_odom(vx, vy, omega, now)

    def _publish_odom(self, vx, vy, omega, stamp):
        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        odom = Odometry()
        odom.header.stamp    = stamp.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id  = 'base_link'
        odom.pose.pose.position.x    = self.x
        odom.pose.pose.position.y    = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x    = vx
        odom.twist.twist.linear.y    = vy
        odom.twist.twist.angular.z   = omega
        self.odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header.stamp    = stamp.to_msg()
        tf.header.frame_id = 'odom'
        tf.child_frame_id  = 'base_link'
        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.rotation.z    = qz
        tf.transform.rotation.w    = qw
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
