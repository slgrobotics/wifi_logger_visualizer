import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'wifi_logger_visualizer'
    package_dir = get_package_share_directory(package_name)
    config_filepath = os.path.join(package_dir, 'config', 'wifi_logger_config.yaml')

    return LaunchDescription([
        Node(
            package=package_name,
            executable='wifi_logger_node.py',
            # Do NOT set name='wifi_logger' here. `ros2 launch` translates
            # name= into a global `-r __node:=X` remap, which renames the
            # node at runtime. But config/wifi_logger_config.yaml uses key
            # `/wifi_logger_node:` — matching the script's self-name via
            # `super().__init__('wifi_logger_node')`. A mismatch makes rclpy
            # silently drop ALL parameters (including wifi_interface,
            # db_path, publish flags, etc.), leaving the node running with
            # code defaults. Symptom: auto-detected interface picks the
            # wrong radio (or an un-associated built-in), iwconfig returns
            # None every tick, timer_callback skips insertion at DEBUG
            # level, and the node runs silently with zero rows written and
            # no visible error. Letting the script self-name preserves the
            # YAML→node name match so parameters take effect.
            parameters=[config_filepath],
            # arguments=['--ros-args', '--log-level', 'DEBUG'],
            output='screen'
        )
    ])