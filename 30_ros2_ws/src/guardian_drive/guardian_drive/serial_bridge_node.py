# MIT License
# GUARDIAN — StarkHacks 2026
# Node: serial_bridge_node
# Purpose: sends RPM targets to two ESP32 boards over USB serial, reads encoder feedback, publishes /odom

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

        self.declare_parameter('serial_port_front', '/dev/ttyUSB0')
        self.declare_parameter('serial_port_rear',  '/dev/ttyUSB1')
        self.declare_parameter('baud_rate',          115200)
        self.declare_parameter('serial_timeout',     1.0)
        self.declare_parameter('wheel_radius',       0.0748)
        self.declare_parameter('wheel_base_length',  0.25)
        self.declare_parameter('wheel_base_width',   0.20)

        port_front = self.get_parameter('serial_port_front').value
        port_rear  = self.get_parameter('serial_port_rear').value
        baud       = self.get_parameter('baud_rate').value
        timeout    = self.get_parameter('serial_timeout').value

        self.ser_front = self._open_port(port_front, baud, timeout)
        self.ser_rear  = self._open_port(port_rear,  baud, timeout)

        self.sub = self.create_subscription(
            Float32MultiArray, '/wheel_rpm', self.rpm_callback, 10)
        self.odom_pub    = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.x = self.y = self.yaw = 0.0
        self.last_time = self.get_clock().now()

        # Last known encoder ticks from each board (for odometry merging)
        self._fl = 0; self._fr = 0
        self._bl = 0; self._br = 0

        self.create_timer(0.02, self.read_encoders)  # 50 Hz

        self.get_logger().info('serial_bridge_node started (FRONT=%s, REAR=%s)', port_front, port_rear)

    # ------------------------------------------------------------------
    def _open_port(self, port: str, baud: int, timeout: float):
        try:
            s = serial.Serial(port, baud, timeout=timeout)
            self.get_logger().info(f'Opened serial port {port} at {baud} baud')
            return s
        except serial.SerialException as e:
            self.get_logger().warn(f'Could not open serial port {port}: {e}')
            return None

    # ------------------------------------------------------------------
    def rpm_callback(self, msg: Float32MultiArray):
        if len(msg.data) < 4:
            self.get_logger().warn('wheel_rpm message has fewer than 4 values')
            return

        fl, fr, bl, br = (int(round(v)) for v in msg.data[:4])

        self._write_safe(self.ser_front, f'M1:{fl} M2:{fr}\n', 'FRONT')
        self._write_safe(self.ser_rear,  f'M1:{bl} M2:{br}\n', 'REAR')

    def _write_safe(self, ser, line: str, label: str):
        if ser is None:
            return
        try:
            ser.write(line.encode())
        except serial.SerialException as e:
            self.get_logger().error(f'Serial write error ({label}): {e}')

    # ------------------------------------------------------------------
    def read_encoders(self):
        updated = False

        updated |= self._read_board(self.ser_front, 'FRONT', is_front=True)
        updated |= self._read_board(self.ser_rear,  'REAR',  is_front=False)

        if updated:
            self._compute_odom()

    def _read_board(self, ser, label: str, is_front: bool) -> bool:
        if ser is None:
            return False
        try:
            if not ser.in_waiting:
                return False
            raw = ser.readline()
        except serial.SerialException as e:
            self.get_logger().error(f'Serial read error ({label}): {e}')
            return False

        line = raw.decode(errors='replace').strip()

        if not line.startswith('ENC:'):
            # Log heartbeat lines at debug level, ignore everything else
            if 'alive' in line:
                self.get_logger().debug(f'Heartbeat ({label}): {line}')
            return False

        try:
            parts = {}
            for token in line[4:].split():
                k, _, v = token.partition(':')
                parts[k] = int(v)
            m1 = parts['M1']
            m2 = parts['M2']
        except Exception as e:
            self.get_logger().warn(f'Failed to parse encoder line from {label} "{line}": {e}')
            return False

        if is_front:
            self._fl = m1
            self._fr = m2
            self.get_logger().debug(f'ENC FRONT FL={m1} FR={m2}')
        else:
            self._bl = m1
            self._br = m2
            self.get_logger().debug(f'ENC REAR  BL={m1} BR={m2}')

        return True

    # ------------------------------------------------------------------
    def _compute_odom(self):
        r = self.get_parameter('wheel_radius').value
        L = self.get_parameter('wheel_base_length').value / 2.0
        W = self.get_parameter('wheel_base_width').value / 2.0

        k = 2.0 * math.pi / 60.0
        fl = self._fl * k; fr = self._fr * k
        bl = self._bl * k; br = self._br * k

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
