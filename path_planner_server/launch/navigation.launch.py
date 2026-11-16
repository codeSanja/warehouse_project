import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def navigation_nodes(suffix, sim_time, condition):

    planner_dir = get_package_share_directory('path_planner_server')

    map_file = os.path.join(
        get_package_share_directory('map_server'),
        'config',
        'warehouse_map_' + suffix + '.yaml'
    )

    amcl_config = os.path.join(
        get_package_share_directory('localization_server'),
        'config',
        'amcl_config_' + suffix + '.yaml'
    )

    planner_config = os.path.join(planner_dir, 'config', 'planner_' + suffix + '.yaml')
    controller_config = os.path.join(planner_dir, 'config', 'controller_' + suffix + '.yaml')
    recoveries_config = os.path.join(planner_dir, 'config', 'recoveries_' + suffix + '.yaml')
    bt_navigator_config = os.path.join(planner_dir, 'config', 'bt_navigator_' + suffix + '.yaml')
    rviz_config = os.path.join(planner_dir, 'rviz', 'navigation.rviz')

    return [
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                {'use_sim_time': sim_time},
                {'yaml_filename': map_file}
            ],
            condition=condition
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[amcl_config, {'use_sim_time': sim_time}],
            condition=condition
        ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[planner_config, {'use_sim_time': sim_time}],
            condition=condition
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[controller_config, {'use_sim_time': sim_time}],
            condition=condition
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[recoveries_config, {'use_sim_time': sim_time}],
            condition=condition
        ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[bt_navigator_config, {'use_sim_time': sim_time}],
            condition=condition
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': sim_time}],
            condition=condition
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            output='screen',
            parameters=[{
                'use_sim_time': sim_time,
                'autostart': True,
                'node_names': [
                    'map_server',
                    'amcl',
                    'planner_server',
                    'controller_server',
                    'behavior_server',
                    'bt_navigator'
                ]
            }],
            condition=condition
        )
    ]


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='True',
                description='True for simulation, False for the real robot'
            )
        ]
        + navigation_nodes('sim', True, IfCondition(use_sim_time))
        + navigation_nodes('real', False, UnlessCondition(use_sim_time))
    )