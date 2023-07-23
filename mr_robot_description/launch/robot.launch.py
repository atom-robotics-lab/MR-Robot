import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue



def generate_launch_description():	

	# get the required paths of packages & files
	pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
	pkg_mr_robot_desc = get_package_share_directory('mr_robot_description')
	xacro_path = pkg_mr_robot_desc + '/urdf/mr_robot.xacro'
	
	# TODO: take rviz config file as launch arg 
	# use this one as default
	rviz_config = pkg_mr_robot_desc + '/config/urdf.rviz'
	bridge_config = pkg_mr_robot_desc + '/config/bridge.yaml'

	# launch configs to use launch args
	use_sim_time = LaunchConfiguration('use_sim_time')
	with_rviz = LaunchConfiguration('rviz')
	with_bridge = LaunchConfiguration('with_bridge')
	kinect_enabled = LaunchConfiguration('kinect_enabled')
	lidar_enabled = LaunchConfiguration('lidar_enabled')
	camera_enabled = LaunchConfiguration('camera_enabled')

	# create urdf from xacro 
	robot_xacro_config = xacro.process_file(xacro_path)
	robot_urdf = robot_xacro_config.toxml()

	# joint state publisher
	state_publisher = Node(package = 'robot_state_publisher',
								executable = 'robot_state_publisher',
								parameters = [{'robot_description': ParameterValue(Command( \
											['xacro ', os.path.join(pkg_mr_robot_desc, 'urdf/mr_robot.xacro'),
											' kinect_enabled:=', kinect_enabled,
											' lidar_enabled:=', lidar_enabled,
											' camera_enabled:=', camera_enabled,
											]), value_type=str)}]
								)

	# spawn robot in gz sim using urdf
	spawn_robot = Node(package = "ros_gz_sim",
                           executable = "create",
                           arguments = ["-topic", "/robot_description",
                                        "-name", "mr_robot",
                                        "-allow_renaming", "true",
                                        "-z", "0.0",
                                        "-x", "2.0",
                                        "-y", "0.0",
                                        "-Y", "-1.57",
                                        ],
							output='screen'
                           )


	# launch rviz node if rviz parameter was set to true
	rviz = Node(package='rviz2',
				executable='rviz2',
				name='rviz',
#				output='screen',
				arguments=['-d' + rviz_config],
				condition=IfCondition(with_rviz))
	
	
			

	# parameter bridge node to bridge different gz and tos 2 topics
	ros_gz_bridge = Node(package="ros_gz_bridge", 
				executable="parameter_bridge",
                parameters = [
                    {'config_file': bridge_config}],
				condition=IfCondition(with_bridge)
                )

	
	lidar_stf = Node(package='tf2_ros', executable='static_transform_publisher',
            name = 'lidar_stf',
                arguments = [
                    '0', '0', '0', '0', '0', '0', '1',
                    'lidar_1',
                    'mr_robot/base_link/front_rplidar'
            ])

	map_stf = Node(package='tf2_ros', executable='static_transform_publisher',
            name = 'map_stf',
                arguments = [
                    '2.0', '0', '0', '0', '0', '-1.57', '100',
                    'map',
                    'odom'
            ])

	kinect_stf = Node(package = 'tf2_ros', executable = 'static_transform_publisher',
                     namespace = 'mr_robot_description',
                     name = 'kinect_stf',
                     arguments = ['0', '0', '0', '0', '0', '0', '1',
                                  'kinect_camera',
                                  'mr_robot/base_link/kinect_camera'
                                  ]
                      )

	camera_stf = Node(package = 'tf2_ros', executable = 'static_transform_publisher',
                     namespace = 'mr_robot_description',
                     name = 'camera_stf',
                     arguments = ['0', '0', '0', '0', '0', '0', '1',
                                  'camera_link',
                                  'mr_robot/base_link/camera_link'
                                  ]
                      )

	# use_sim_time launch argument
	arg_use_sim_time = DeclareLaunchArgument('use_sim_time',
											default_value='true',
											description="Enable sim time from /clock")
	
	# argument to specify if rviz needs to be launched
	arg_with_rviz = DeclareLaunchArgument('rviz', default_value='false',
											description="Set true to launch rviz")

	# argument to specify if bridge needs to be launched
	arg_with_bridge = DeclareLaunchArgument('with_bridge', default_value='true',
											description="Set true to bridge ROS 2 & Gz topics")

	# argument to specify if the kinect camera needs to be added to the bot
	kinect_enabled_arg = DeclareLaunchArgument("kinect_enabled", default_value = 'true',
											description="Set true to add kinect camera to bot")

	# argument to specify if the lidar needs to be added to the bot
	lidar_enabled_arg = DeclareLaunchArgument("lidar_enabled", default_value = 'true',
											description="Set true to add lidar to bot")

	# argument to specify if the 2D camera needs to be added to the bot
	camera_enabled_arg = DeclareLaunchArgument("camera_enabled", default_value = 'true',
											description="Set true to add 2D camera to bot")

	
	
	return LaunchDescription([
		arg_use_sim_time,
		arg_with_rviz,
		arg_with_bridge,
		kinect_enabled_arg,
		lidar_enabled_arg,
		camera_enabled_arg,
		spawn_robot,
		ros_gz_bridge,
		rviz,
		state_publisher,
		lidar_stf,
		map_stf,
		kinect_stf,
		camera_stf
	])