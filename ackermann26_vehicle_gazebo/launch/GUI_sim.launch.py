from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
import os
from ament_index_python.packages import get_package_share_path, get_package_share_directory


def generate_launch_description():

    robot_description_pkg = get_package_share_path("ackermann26_vehicle_description")
    gazebo_pkg = get_package_share_path("ackermann26_vehicle_gazebo")

    urdf_path = os.path.join(robot_description_pkg, 'urdf', 'mobile_robot.urdf.xacro')
    rviz_config_path = os.path.join(robot_description_pkg, 'rviz', 'Final_config.rviz')
    bridge_config_path = os.path.join(gazebo_pkg, 'config', 'ros_bridge.yaml')

    gz_sim_launch_path = os.path.join(
        get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock'
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='vehicle_world.sdf',
        description='World file name, searched in the worlds/ directory of this package'
    )

    worlds_dir = os.path.join(gazebo_pkg, 'worlds')

    spawn_x_arg = DeclareLaunchArgument('x', default_value='0.0')
    spawn_y_arg = DeclareLaunchArgument('y', default_value='0.0')
    spawn_z_arg = DeclareLaunchArgument('z', default_value='0.0')
    spawn_yaw_arg = DeclareLaunchArgument('yaw', default_value='0.0')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    robot_state_publisher = Node(
        name='robot_state_publisher',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )

    joint_state_publisher_gui = Node(
        name='joint_state_publisher_gui',
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    rviz_node = Node(
        name='rviz2',
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_sim_launch_path),
        launch_arguments={
            'gz_args': [worlds_dir, '/', LaunchConfiguration('world'), ' -r -v 4']
        }.items()
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'ackermann_vehicle',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
            '-Y', LaunchConfiguration('yaw'),
        ],
        output='screen'
    )

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        parameters=[{'config_file': bridge_config_path}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        world_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        spawn_yaw_arg,
        gz_sim,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node,
        spawn_entity,
        bridge_node,
    ])
