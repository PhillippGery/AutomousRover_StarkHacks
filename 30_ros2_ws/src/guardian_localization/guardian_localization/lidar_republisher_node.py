# MIT License
# GUARDIAN — StarkHacks 2026
# Node: lidar_republisher_node
# Owner: Phillipp
# Purpose: republishes Scanse Sweep scan data to /scan topic for Nav2

import rclpy
from rclpy.node import Node
# TODO: import message types needed
# from sensor_msgs.msg import LaserScan


class LidarRepublisherNode(Node):
    def __init__(self):
        super().__init__('lidar_republisher_node')
        self.get_logger().info('lidar_republisher_node started')

        # TODO: declare parameters
        # self.declare_parameter('input_topic', '/sweep/scan')
        # self.declare_parameter('output_topic', '/scan')

        # TODO: create subscribers
        # self.sub = self.create_subscription(
        #     LaserScan, '/sweep/scan', self.scan_callback, 10)

        # TODO: create publishers
        # self.pub = self.create_publisher(LaserScan, '/scan', 10)

    # TODO: implement callbacks
    # def scan_callback(self, msg):
    #     # Optionally transform frame_id or filter ranges here
    #     # msg.header.frame_id = 'laser'
    #     self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LidarRepublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
