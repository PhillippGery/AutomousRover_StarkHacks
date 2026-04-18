# MIT License
# GUARDIAN — StarkHacks 2026
# Node: lidar_republisher_node
# Purpose: republishes Scanse Sweep scan to /scan for Nav2, fixes frame_id

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarRepublisherNode(Node):
    def __init__(self):
        super().__init__('lidar_republisher_node')

        self.declare_parameter('input_topic', '/sweep/scan')
        self.declare_parameter('output_topic', '/scan')
        self.declare_parameter('frame_id', 'laser')

        in_topic  = self.get_parameter('input_topic').value
        out_topic = self.get_parameter('output_topic').value

        self.pub = self.create_publisher(LaserScan, out_topic, 10)
        self.sub = self.create_subscription(LaserScan, in_topic, self.scan_callback, 10)

        self.get_logger().info(
            f'lidar_republisher_node: {in_topic} → {out_topic}')

    def scan_callback(self, msg: LaserScan):
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value
        self.pub.publish(msg)


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
