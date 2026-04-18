# MIT License
# GUARDIAN — StarkHacks 2026
# Node: keyboard_teleop_node
# Purpose: WASD keyboard control → /cmd_vel

import sys
import tty
import termios
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

KEYS = {
    'w': ( 1,  0,  0),
    's': (-1,  0,  0),
    'a': ( 0,  1,  0),
    'd': ( 0, -1,  0),
    'q': ( 0,  0,  1),
    'e': ( 0,  0, -1),
}

BANNER = """
GUARDIAN Keyboard Teleop
------------------------
  w     forward
  s     backward
  a     strafe left
  d     strafe right
  q     rotate left
  e     rotate right
  space stop
  +/-   speed up/down
  x     quit
------------------------
"""


def get_key(fd):
    return sys.stdin.read(1)


class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('keyboard_teleop_node')
        self.declare_parameter('linear_speed', 0.05)
        self.declare_parameter('angular_speed', 1.0)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('keyboard_teleop_node started')

    def run(self):
        lin = self.get_parameter('linear_speed').value
        ang = self.get_parameter('angular_speed').value
        speed_scale = 0.3  # start at 30% (~900 ticks/sec), use +/- to adjust

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        print(BANNER)
        print(f'Speed: {speed_scale*100:.0f}%  (use +/- to adjust)')
        try:
            tty.setraw(fd)
            while rclpy.ok():
                key = get_key(fd)
                twist = Twist()
                if key in KEYS:
                    vx, vy, oz = KEYS[key]
                    twist.linear.x  = vx * lin * speed_scale
                    twist.linear.y  = vy * lin * speed_scale
                    twist.angular.z = oz * ang * speed_scale
                elif key in ('+', '='):
                    speed_scale = min(1.0, speed_scale + 0.1)
                    print(f'\rSpeed: {speed_scale*100:.0f}%  ', end='', flush=True)
                    continue
                elif key == '-':
                    speed_scale = max(0.1, speed_scale - 0.1)
                    print(f'\rSpeed: {speed_scale*100:.0f}%  ', end='', flush=True)
                    continue
                elif key in (' ', 'k'):
                    pass  # zero twist = stop
                elif key in ('x', '\x03'):
                    break
                else:
                    continue
                self.pub.publish(twist)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
            self.pub.publish(Twist())  # stop on exit


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleopNode()
    try:
        node.run()
    except Exception as e:
        node.get_logger().error(str(e))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
