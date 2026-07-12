from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
import os

def generate_launch_description():
    ld = LaunchDescription()

    package_name = 'wifi_logger_visualizer'
    package_dir = get_package_share_directory(package_name)
    config_filepath = os.path.join(package_dir, 'config', 'wifi_logger_config.yaml')

    # Declare conditions:
    run_logger = LaunchConfiguration('run_logger')
    run_logger_arg = DeclareLaunchArgument(
        'run_logger',
        default_value='True',
        description='Run the wifi logger node'
    )
    ld.add_action(run_logger_arg)
    
    run_visualizer = LaunchConfiguration('run_visualizer')
    run_visualizer_arg = DeclareLaunchArgument(
        'run_visualizer',
        default_value='True',
        description='Run the wifi visualizer node'
    )
    ld.add_action(run_visualizer_arg)
    
    run_heatmapper = LaunchConfiguration('run_heatmapper')
    run_heatmapper_arg = DeclareLaunchArgument(
        'run_heatmapper',
        default_value='True',
        description='Run the heat mapper node'
    )
    ld.add_action(run_heatmapper_arg)
    
    ld.add_action(LogInfo(msg=["[wifi_logger_visualizer.launch.py] ",
                               " run_logger: ", run_logger,
                               ", run_visualizer: ", run_visualizer,
                               ", run_heatmapper: ", run_heatmapper]))

    # Declare launch arguments for nodes:
    db_path_arg = DeclareLaunchArgument(
        'db_path',
        default_value=os.path.join(os.getcwd(), 'wifi_data.db'),
        description='Path to the SQLite database file'
    )
    
    publish_frequency_arg = DeclareLaunchArgument(
        'publish_frequency',
        default_value='1.0',
        description='Frequency at which to publish costmaps (Hz)'
    )
    
    db_check_frequency_arg = DeclareLaunchArgument(
        'db_check_frequency',
        default_value='2.0',
        description='Frequency at which to check for database updates (Hz)'
    )
    
    max_interpolation_distance_arg = DeclareLaunchArgument(
        'max_interpolation_distance',
        default_value='1.0',
        description='Maximum distance for interpolation in meters'
    )
    
    enable_link_quality_arg = DeclareLaunchArgument(
        'enable_link_quality',
        default_value='true',
        description='Enable link quality costmap'
    )
    
    enable_signal_level_arg = DeclareLaunchArgument(
        'enable_signal_level',
        default_value='true',
        description='Enable signal level costmap'
    )
    
    enable_bit_rate_arg = DeclareLaunchArgument(
        'enable_bit_rate',
        default_value='true',
        description='Enable bit rate costmap'
    )
    
    costmap_topic_arg = DeclareLaunchArgument(
        'costmap_topic',
        default_value='/global_costmap/costmap',
        description='Topic to read costmap dimensions from'
    )

    for action in [
        db_path_arg,
        publish_frequency_arg,
        db_check_frequency_arg,
        max_interpolation_distance_arg,
        enable_link_quality_arg,
        enable_signal_level_arg,
        enable_bit_rate_arg,
        costmap_topic_arg,
    ]:
        ld.add_action(action)
    
    wifi_loger_node = Node(
        condition=IfCondition(run_logger),
        package=package_name,
        executable='wifi_logger_node.py',
        name='wifi_logger_node',
        parameters=[
            config_filepath,
            {
                'db_path': LaunchConfiguration('db_path'),
            }
        ],
        # arguments=['--ros-args', '--log-level', 'DEBUG'],
        output='screen'
    )
    ld.add_action(wifi_loger_node)

    wifi_visualizer_node = Node(
        condition=IfCondition(run_visualizer),
        package=package_name,
        executable='wifi_visualizer_node.py',
        name='wifi_visualizer_node',
        output='screen',
        parameters=[
            config_filepath,
            {
                'db_path': LaunchConfiguration('db_path'),
                'publish_frequency': LaunchConfiguration('publish_frequency'),
                'db_check_frequency': LaunchConfiguration('db_check_frequency'),
                'max_interpolation_distance': LaunchConfiguration('max_interpolation_distance'),
                'enable_link_quality': LaunchConfiguration('enable_link_quality'),
                'enable_signal_level': LaunchConfiguration('enable_signal_level'),
                'enable_bit_rate': LaunchConfiguration('enable_bit_rate'),
                'costmap_topic': LaunchConfiguration('costmap_topic')
            }
        ]
    )
    ld.add_action(wifi_visualizer_node)

    heat_mapper_node = Node(
        condition=IfCondition(run_heatmapper),
        package=package_name,
        executable='heat_mapper_node.py',
        name='heat_mapper_node',
        output='screen',
        parameters=[
            config_filepath,
            {
                'db_path': LaunchConfiguration('db_path'),
                'costmap_topic': LaunchConfiguration('costmap_topic')
            }
        ]
    )
    ld.add_action(heat_mapper_node)


    return ld
