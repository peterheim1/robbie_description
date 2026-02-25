# launch/view_robbie_with_gui.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command

def generate_launch_description():
    default_model = PathJoinSubstitution([
        FindPackageShare('robbie_description'), 'urdf', 'robbie.urdf.xacro'   # can also be .xacro
    ])

    urdf = LaunchConfiguration('urdf')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'),  # resolves full path to xacro
            ' ',
            urdf                           # the model path (URDF or Xacro)
        ]),
        value_type=str
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}],
    )

    jsp_gui = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'urdf',
            default_value=default_model,
            description='Path to the robot URDF/Xacro to be expanded by xacro.',
        ),
        rsp,
        jsp_gui,
    ])

