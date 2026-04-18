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

        self.declare_parameter('serial_port_front', '/dev/ttyACM0')
        self.declare_parameter('serial_port_rear',  '/dev/ttyACM1')
        self.declare_parameter('baud_rate',          115200)
        self.declare_parameter('serial_timeout',     1.0)
        self.declare_parameter('wheel_radius',       0.048)
        self.declare_parameter('wheel_base_length',  0.25)
        self.declare_parameter('wheel_base_width',   0.20)
        self.declare_parameter('cpr',                4.0)   # encoder counts per wheel rev
        self.declare_parameter('sim_mode',           False)

        self.sim_mode  = self.get_parameter('sim_mode').value
        port_front     = self.get_parameter('serial_port_front').value
        port_rear      = self.get_parameter('serial_port_rear').value
        baud           = self.get_parameter('baud_rate').value
        timeout        = self.get_parameter('serial_timeout').value
        self.cpr       = self.get_parameter('cpr').value

        if self.sim_mode:
            self.ser_front = self.ser_rear = None
            self.get_logger().warn('sim_mode=true — serial disabled, publishing zero odometry')
        else:
            self.ser_front = self._open_port(port_front, baud, timeout)
            self.ser_rear  = self._open_port(port_rear,  baud, timeout)

        self.sub = self.create_subscription(
            Float32MultiArray, '/wheel_rpm', self.rpm_callback, 10)
        self.odom_pub       = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.x = self.y = self.yaw = 0.0
        self.last_time = self.get_clock().now()

        # Cumulative tick tracking for velocity computation (per-board timestamps)
        self._prev_fl = self._prev_fr = 0
        self._prev_bl = self._prev_br = 0
        self._prev_tick_time_front = self.get_clock().now()
        self._prev_tick_time_rear  = self.get_clock().now()

        # Latest velocity estimates (ticks/sec)
        self._vel_fl = self._vel_fr = 0.0
        self._vel_bl = self._vel_br = 0.0

        self.create_timer(0.02, self.read_encoders)  # 50 Hz

        self.get_logger().info(
            f'serial_bridge_node started (FRONT={port_front}, REAR={port_rear})')

    def _open_port(self, port, baud, timeout):
        try:
            s = serial.Serial(port, baud, timeout=timeout)
            self.get_logger().info(f'Opened {port} at {baud} baud')
            return s
        except serial.SerialException as e:
            self.get_logger().warn(f'Could not open {port}: {e}')
            return None

    # ── Commands ────────────────────────────────────────────────────────────────
    def rpm_callback(self, msg: Float32MultiArray):
        if len(msg.data) < 4:
            self.get_logger().warn('wheel_rpm: need 4 values')
            return
        fl_rpm, fr_rpm, bl_rpm, br_rpm = msg.data[:4]

        # boards accept ticks/sec — convert from RPM
        fl = int(round(fl_rpm * self.cpr / 60.0))
        fr = int(round(fr_rpm * self.cpr / 60.0))
        bl = int(round(bl_rpm * self.cpr / 60.0))
        br = int(round(br_rpm * self.cpr / 60.0))

        self._write_safe(self.ser_front, f'M1:{fl} M2:{fr}\n', 'FRONT')
        self._write_safe(self.ser_rear,  f'M1:{bl} M2:{br}\n', 'REAR')

    def _write_safe(self, ser, line, label):
        if ser is None:
            return
        try:
            ser.write(line.encode())
        except serial.SerialException as e:
            self.get_logger().error(f'Serial write ({label}): {e}')

    # ── Encoder reading ──────────────────────────────────────────────────────────
    def read_encoders(self):
        if self.sim_mode:
            self._publish_odom(0.0, 0.0, 0.0, self.get_clock().now())
            return

        updated = False
        updated |= self._read_board(self.ser_front, 'FRONT', is_front=True)
        updated |= self._read_board(self.ser_rear,  'REAR',  is_front=False)
        if updated:
            self._compute_odom()

    def _read_board(self, ser, label, is_front):
        if ser is None or not ser.in_waiting:
            return False
        try:
            raw = ser.readline()
        except serial.SerialException as e:
            self.get_logger().error(f'Serial read ({label}): {e}')
            return False

        line = raw.decode(errors='replace').strip()

        if not line.startswith('ENC:'):
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
            self.get_logger().warn(f'Parse error ({label}) "{line}": {e}')
            return False

        now = self.get_clock().now()
        if is_front:
            dt = (now - self._prev_tick_time_front).nanoseconds / 1e9
            if dt <= 0:
                return False
            self._vel_fl = (m1 - self._prev_fl) / dt
            self._vel_fr = (m2 - self._prev_fr) / dt
            self._prev_fl = m1
            self._prev_fr = m2
            self._prev_tick_time_front = now
        else:
            dt = (now - self._prev_tick_time_rear).nanoseconds / 1e9
            if dt <= 0:
                return False
            self._vel_bl = (m1 - self._prev_bl) / dt
            self._vel_br = (m2 - self._prev_br) / dt
            self._prev_bl = m1
            self._prev_br = m2
            self._prev_tick_time_rear = now

        return True

    # ── Odometry ─────────────────────────────────────────────────────────────────
    def _compute_odom(self):
        r = self.get_parameter('wheel_radius').value
        L = self.get_parameter('wheel_base_length').value / 2.0
        W = self.get_parameter('wheel_base_width').value / 2.0

        # ticks/sec → rad/s
        k = 2.0 * math.pi / self.cpr
        fl = self._vel_fl * k
        fr = self._vel_fr * k
        bl = self._vel_bl * k
        br = self._vel_br * k

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
