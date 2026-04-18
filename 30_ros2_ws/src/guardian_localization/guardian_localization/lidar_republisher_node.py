# MIT License
# GUARDIAN — StarkHacks 2026
# Node: lidar_republisher_node
# Purpose: republishes Scanse Sweep scan to /scan for Nav2, fixes frame_id

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import LaserScan


class LidarRepublisherNode(Node):
    def __init__(self):
        super().__init__('lidar_republisher_node')

        self.declare_parameter('input_topic', '/sweep/scan')
        self.declare_parameter('output_topic', '/scan')
        self.declare_parameter('frame_id', 'laser')
        self.declare_parameter('timestamp_offset_sec', 0.05)

        in_topic  = self.get_parameter('input_topic').value
        out_topic = self.get_parameter('output_topic').value

        # Subscribe with BEST_EFFORT to match sweep scanner publisher
        sub_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10)
        # Publish with RELIABLE so SLAM toolbox can subscribe
        pub_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10)

        self.pub = self.create_publisher(LaserScan, out_topic, pub_qos)
        self.sub = self.create_subscription(LaserScan, in_topic, self.scan_callback, sub_qos)

        self.get_logger().info(
            f'lidar_republisher_node: {in_topic} → {out_topic}')

    def scan_callback(self, msg: LaserScan):
        offset_sec = float(self.get_parameter('timestamp_offset_sec').value)
        stamp = self.get_clock().now() - Duration(seconds=offset_sec)
        msg.header.stamp = stamp.to_msg()
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
