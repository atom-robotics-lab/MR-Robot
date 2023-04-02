import os
import sys

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_mr_robot_desc = get_package_share_directory('mr_robot_description')
    pkg_mr_robot_gazebo = get_package_share_directory('mr_robot_gazebo')

    # Default world to use
    # TODO: find a better way to create path with given world name arg
    world_name = "small_room.sdf"

    for arg in sys.argv:
        if arg.startswith("world:="):
            world_name = arg.split(":=")[1]

    world_path = pkg_mr_robot_gazebo + "/worlds/small_room.sdf"

    # launch GZ Sim with empty world
    gz_sim = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
                ),
                launch_arguments={
                    'gz_args' : world_path + " -v 4"
                }.items()          
            )
    
    # spawn robot with rviz
    robot = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_mr_robot_desc, 'launch', 'robot.launch.py')
                ),
                launch_arguments={
                    'rviz': 'true',
                    'with_bridge': 'true'
                }.items()
            )

    # world name launch argument
    arg_world_name = DeclareLaunchArgument('world', default_value='small_room.sdf',
                                            description="Name of the world to launch")
    
    return LaunchDescription([
        arg_world_name,
        gz_sim,
        robot
    ])