import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import LaunchConfigurationEquals, LaunchConfigurationNotEquals
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    map_file = PathJoinSubstitution([
        get_package_share_directory('map_server'),
        'config',
        LaunchConfiguration('map_file')
    ])

    amcl_config_sim = os.path.join(
        get_package_share_directory('localization_server'),
        'config',
        'amcl_config_sim.yaml'
    )

    amcl_config_real = os.path.join(
        get_package_share_directory('localization_server'),
        'config',
        'amcl_config_real.yaml'
    )

    rviz_config = os.path.join(
        get_package_share_directory('localization_server'),
        'rviz',
        'localization.rviz'
    )

    rviz_node_sim = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=LaunchConfigurationEquals('map_file', 'warehouse_map_sim.yaml')
    )

    rviz_node_real = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': False}],
        condition=LaunchConfigurationNotEquals('map_file', 'warehouse_map_sim.yaml')
    )

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'yaml_filename': map_file}
        ]
    )

    amcl_node_sim = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_config_sim,
            {'use_sim_time': True}
        ],
        condition=LaunchConfigurationEquals('map_file', 'warehouse_map_sim.yaml')
    )

    amcl_node_real = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_config_real,
            {'use_sim_time': False}
        ],
        condition=LaunchConfigurationNotEquals('map_file', 'warehouse_map_sim.yaml')
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'autostart': True},
            {'node_names': ['map_server', 'amcl']}
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map_file',
            default_value='warehouse_map_sim.yaml',
            description='Map yaml file name inside map_server/config'
        ),
        map_server_node,
        amcl_node_sim,
        amcl_node_real,
        lifecycle_manager_node,
        rviz_node_sim,
        rviz_node_real
    ])