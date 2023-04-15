import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition


def generate_launch_description():
	pkg_mr_robot_nav = get_package_share_directory('mr_robot_nav')
	pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

	use_sim_time = LaunchConfiguration('use_sim_time', default='true')
	with_rviz = LaunchConfiguration('with_rviz', default='true')
	map_yaml_file = LaunchConfiguration('map',
					default=os.path.join(pkg_mr_robot_nav, 'maps', 'map.yaml'))
	nav2_config_file = LaunchConfiguration('params', 
						default=os.path.join(pkg_mr_robot_nav, 'config', 'nav2.yaml'))
	# rviz_config_file = LaunchConfiguration('rviz_config',
	# 					default=os.path.join(pkg_nav2_bringup, 'rviz', 'nav2_default_view.rviz'))

	# nav2 bringup launch file
	nav2_bringup_launch_file = IncludeLaunchDescription(
					PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')),
					launch_arguments={
						'map': map_yaml_file,
						'use_sim_time': use_sim_time,
						'params_file': nav2_config_file}.items(),
				)

	# rviz2
	# rviz2 = Node(package='rviz2', executable='rviz2',
	# 				name='rviz2',
	# 				arguments=['-d', rviz_config_file],
	# 				parameters=[{'use_sim_time': use_sim_time}],
	# 				output='screen',
	# 				condition=IfCondition(with_rviz))	
	
	return LaunchDescription([
		DeclareLaunchArgument('map',
					default_value=map_yaml_file,
					description="/home/noemoji041/ros_workspaces/ros2_ws/src/MR-Robot/mr_robot_nav/maps/"),
		DeclareLaunchArgument('params_file',
		     		default_value=nav2_config_file,
		     		description="/home/noemoji041/ros_workspaces/ros2_ws/src/MR-Robot/mr_robot_nav/config/"),
		DeclareLaunchArgument('use_sim_time',
                                default_value=use_sim_time,
                                description="Use sim clock or not"),
		# DeclareLaunchArgument('with_rviz',
		# 						default_value=with_rviz,
		# 						description='Launch rviz2'),
		nav2_bringup_launch_file,
		# rviz2
		])
