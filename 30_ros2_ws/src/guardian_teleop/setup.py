from setuptools import setup
import os
from glob import glob

package_name = 'guardian_teleop'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Phillipp Gery',
    maintainer_email='phillipp@example.com',
    description='Meta Quest 3 and joystick teleoperation for GUARDIAN',
    license='MIT',
    entry_points={
        'console_scripts': [
            'quest_bridge_node = guardian_teleop.quest_bridge_node:main',
            'joystick_fallback_node = guardian_teleop.joystick_fallback_node:main',
        ],
    },
)
