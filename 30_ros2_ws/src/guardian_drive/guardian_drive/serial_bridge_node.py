# MIT License
# GUARDIAN — StarkHacks 2026
# Node: serial_bridge_node
# Owner: Phillipp
# Purpose: sends RPM targets to Arduino over USB serial, reads encoder feedback, publishes /odom

import rclpy
from rclpy.node import Node
# TODO: import message types needed
# from std_msgs.msg import Float32MultiArray
# from nav_msgs.msg import Odometry
# import serial


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')
        self.get_logger().info('serial_bridge_node started')

        # TODO: declare parameters
        # self.declare_parameter('serial_port', '/dev/ttyUSB0')
        # self.declare_parameter('serial_baud', 115200)

        # TODO: open serial port
        # port = self.get_parameter('serial_port').value
        # baud = self.get_parameter('serial_baud').value
        # self.ser = serial.Serial(port, baud, timeout=0.1)

        # TODO: create subscribers
        # self.sub = self.create_subscription(
        #     Float32MultiArray, '/wheel_rpms', self.rpm_callback, 10)

        # TODO: create publishers
        # self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # TODO: create timer for reading encoder feedback
        # self.timer = self.create_timer(0.02, self.read_encoders)  # 50 Hz

    # TODO: implement callbacks
    # def rpm_callback(self, msg):
    #     fl, fr, bl, br = msg.data
    #     line = f'FL:{int(fl)} FR:{int(fr)} BL:{int(bl)} BR:{int(br)}\n'
    #     self.ser.write(line.encode())

    # def read_encoders(self):
    #     if self.ser.in_waiting:
    #         line = self.ser.readline().decode().strip()
    #         # Parse: "ENC:FL:148 FR:151 BL:-149 BR:-152"
    #         # TODO: parse and integrate into odometry
    #         # TODO: publish nav_msgs/Odometry on /odom


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
