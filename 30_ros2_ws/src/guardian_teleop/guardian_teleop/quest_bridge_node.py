# MIT License
# GUARDIAN — StarkHacks 2026
# Node: quest_bridge_node
# Owner: Victor
# Purpose: receives Quest head tracking and hand data via WebSocket, publishes to ROS2 topics

import rclpy
from rclpy.node import Node
# TODO: import message types needed
# from geometry_msgs.msg import PoseStamped, PoseArray
# import websockets
# import asyncio
# import json


class QuestBridgeNode(Node):
    def __init__(self):
        super().__init__('quest_bridge_node')
        self.get_logger().info('quest_bridge_node started')

        # TODO: declare parameters
        # self.declare_parameter('ws_host', '0.0.0.0')
        # self.declare_parameter('ws_port', 8765)

        # TODO: create publishers
        # self.head_pub = self.create_publisher(PoseStamped, '/quest/head_pose', 10)
        # self.hand_pub = self.create_publisher(PoseArray, '/quest/hand_poses', 10)

        # TODO: start WebSocket server (async)
        # self.timer = self.create_timer(0.033, self.poll_websocket)  # ~30 Hz

    # TODO: implement WebSocket polling / async server
    # def poll_websocket(self):
    #     # Receive JSON from Quest, parse pose data, publish to ROS2 topics
    #     pass


def main(args=None):
    rclpy.init(args=args)
    node = QuestBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
