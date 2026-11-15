import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    config_sim = os.path.join(
        get_package_share_directory('mapping_slam'),
        'config',
        'mapping_config.yaml'
    )

    config_real = os.path.join(
        get_package_share_directory('mapping_slam'),
        'config',
        'mapping_config_real.yaml'
    )

    rviz_config = os.path.join(
        get_package_share_directory('mapping_slam'),
        'rviz',
        'mapping.rviz'
    )

    slam_node_sim = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            config_sim,
            {'use_sim_time': use_sim_time}
        ],
        condition=IfCondition(use_sim_time)
    )

    slam_node_real = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            config_real,
            {'use_sim_time': use_sim_time}
        ],
        condition=UnlessCondition(use_sim_time)
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='True',
            description='True for simulation, False for the real robot'
        ),
        slam_node_sim,
        slam_node_real,
        rviz_node
    ])