from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Default shared params file (same one used by the wifi_logger node)
    default_params_file = os.path.join(
        get_package_share_directory('wifi_logger_visualizer'),
        'config',
        'wifi_logger_config.yaml',
    )

    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Path to a ROS 2 params YAML file (shared with wifi_logger)',
    )

    standalone_arg = DeclareLaunchArgument(
        'standalone',
        default_value='false',
        description='true: matplotlib window; false: publish RViz MarkerArrays',
    )

    # Optional CLI override for the DB path; empty string means "use YAML value".
    db_path_arg = DeclareLaunchArgument(
        'db_path',
        default_value='',
        description='Optional SQLite DB path override (defaults to YAML value)',
    )

    # Launch args always win over YAML in the parameters= list ordering below.
    # We only include db_path in the override dict when the user provided one.
    def _build_node(context):
        overrides = {'standalone': LaunchConfiguration('standalone').perform(context) == 'true'}
        db_path = LaunchConfiguration('db_path').perform(context)
        if db_path:
            overrides['db_path'] = db_path
        return [Node(
            package='wifi_logger_visualizer',
            executable='heat_mapper_node.py',
            name='heat_mapper_node',
            parameters=[LaunchConfiguration('params_file'), overrides],
            output='screen',
        )]

    from launch.actions import OpaqueFunction
    heat_mapper_node = OpaqueFunction(function=_build_node)

    return LaunchDescription([
        params_file_arg,
        standalone_arg,
        db_path_arg,
        heat_mapper_node,
    ])
