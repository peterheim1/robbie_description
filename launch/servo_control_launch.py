#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('robbie_description')

    xacro_file = PathJoinSubstitution(
        [pkg_share, 'urdf', 'robbie.urdf.xacro']
    )
    controllers_yaml = PathJoinSubstitution(
        [pkg_share, 'config', 'controllers.yaml']
    )

    robot_description_content = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'controllers_config',
            default_value=controllers_yaml,
            description='Path to ros2_control controllers config YAML'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': robot_description_content},
                {'use_sim_time': False}
            ]
        ),

        TimerAction(
            period=2.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='ros2_control_node',
                    output='screen',
                    parameters=[
                        {'robot_description': robot_description_content},
                        LaunchConfiguration('controllers_config')
                    ]
                )
            ]
        ),

        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
                    output="screen",
                ),
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['head_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),

                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['left_arm_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),

                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['right_arm_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['right_gripper_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['left_gripper_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),
            ]
        ),
    ])

