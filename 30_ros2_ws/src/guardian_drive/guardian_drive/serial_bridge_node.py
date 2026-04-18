# MIT License
# GUARDIAN — StarkHacks 2026
# Node: serial_bridge_node
# Owner: Phillipp
# Purpose: sends RPM targets to Arduino over USB serial, reads encoder feedback, publishes /odom

import serial

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')

        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('serial_timeout', 1.0)

        port = self.get_parameter('serial_port').value
        baud = self.get_parameter('baud_rate').value
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

        self.get_logger().info('serial_bridge_node started')

    def rpm_callback(self, msg):
        if self.ser is None:
            self.get_logger().warn('Serial port not available, skipping RPM send')
            return

        if len(msg.data) < 4:
            self.get_logger().warn('wheel_rpm message has fewer than 4 values')
            return

        fl, fr, bl, br = (int(round(v)) for v in msg.data[:4])
        line = f'FL:{fl} FR:{fr} BL:{bl} BR:{br}\n'

        try:
            self.ser.write(line.encode())
            raw = self.ser.readline()
            if raw:
                decoded = raw.decode(errors='replace').strip()
                if decoded.startswith('ENC:'):
                    self._handle_encoder_line(decoded)
        except serial.SerialException as e:
            self.get_logger().error(f'Serial error: {e}')
        except Exception as e:
            self.get_logger().error(f'Unexpected serial error: {e}')

        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = 'odom'
        self.odom_pub.publish(odom)

    def _handle_encoder_line(self, line):
        # Expected format: "ENC:FL:148 FR:151 BL:-149 BR:-152"
        try:
            parts = line[len('ENC:'):].split()
            values = {}
            for part in parts:
                label, val = part.split(':')
                values[label] = int(val)
            self.get_logger().info(
                f"Encoders FL={values.get('FL')} FR={values.get('FR')} "
                f"BL={values.get('BL')} BR={values.get('BR')}"
            )
        except Exception as e:
            self.get_logger().warn(f'Failed to parse encoder line "{line}": {e}')


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
