# ackermann26_vehicle_gazebo

ROS 2 package that launches the Ackermann vehicle in Gazebo Sim, loads the test world, spawns the robot from its description, and bridges simulation topics to ROS 2.

## Purpose

This package provides:

- Gazebo Sim launch files.
- The default enclosed vehicle world.
- ROS-Gazebo topic bridge configuration.
- Vehicle spawning from `/robot_description`.
- Optional RViz and joint-state GUI integration.

The robot model itself is provided by the dependency `ackermann26_vehicle_description`.

## Dependencies

The package declares these runtime dependencies:

- `ackermann26_vehicle_description`
- `xacro`
- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `ros_gz_sim`
- `ros_gz_bridge`

It uses the `ament_cmake` build system.

## Build

Build from the colcon workspace root:

```bash
cd /home/nombre_usuario/Workspaces/sm26_ws
source /opt/ros/<ros2-distribution>/setup.bash
colcon build --symlink-install --packages-select \
  ackermann26_vehicle_description ackermann26_vehicle_gazebo
source install/setup.bash
```

The description package is selected as well because this package uses its installed Xacro model and RViz configuration.

## Launch simulation

The standard simulation launch starts Gazebo Sim, `robot_state_publisher`, RViz, the vehicle spawner, and the ROS-Gazebo bridge:

```bash
ros2 launch ackermann26_vehicle_gazebo sim.launch.py
```

To also start `joint_state_publisher_gui`:

```bash
ros2 launch ackermann26_vehicle_gazebo GUI_sim.launch.py
```

The two launch files use the following shared behavior:

1. Expand `mobile_robot.urdf.xacro`.
2. Publish the resulting description on `/robot_description`.
3. Start Gazebo Sim with the selected world.
4. Spawn an entity named `ackermann_vehicle` from `/robot_description`.
5. Start RViz with `Final_config.rviz`.
6. Start `ros_gz_bridge` using `config/ros_bridge.yaml`.

## Launch arguments

Both simulation launch files accept these arguments:

| Argument | Default | Description |
| --- | --- | --- |
| `world` | `vehicle_world.sdf` | World file name in the `worlds` directory. |
| `use_sim_time` | `true` | Use the Gazebo simulation clock for ROS nodes. |
| `x` | `0.0` | Initial vehicle X position in metres. |
| `y` | `0.0` | Initial vehicle Y position in metres. |
| `z` | `0.0` | Initial vehicle Z position in metres. |
| `yaw` | `0.0` | Initial vehicle yaw in radians. |

Example with a different initial pose:

```bash
ros2 launch ackermann26_vehicle_gazebo sim.launch.py \
  x:=0.5 y:=0.0 z:=0.05 yaw:=1.5708
```

A custom world can be selected by placing an SDF file in `worlds/` and passing its file name:

```bash
ros2 launch ackermann26_vehicle_gazebo sim.launch.py world:=my_world.sdf
```

## Default world

`worlds/vehicle_world.sdf` defines:

- A 100 m by 100 m ground plane.
- Directional lighting.
- Gazebo physics, scene, user-command, and contact systems.
- A rectangular track with approximately 4.0 m by 2.6 m outer dimensions.
- Four static walls, each 0.4 m high, intended to be detected by the lidar.

## ROS-Gazebo bridge

The bridge configuration is stored in `config/ros_bridge.yaml`.

### Control and state topics

| ROS topic | Gazebo topic | ROS type | Direction |
| --- | --- | --- | --- |
| `cmd_vel` | `cmd_vel` | `geometry_msgs/msg/Twist` | ROS to Gazebo |
| `odom` | `model/ackermann_vehicle/odometry` | `nav_msgs/msg/Odometry` | Gazebo to ROS |
| `joint_states` | `joint_states` | `sensor_msgs/msg/JointState` | Gazebo to ROS |
| `clock` | `clock` | `rosgraph_msgs/msg/Clock` | Gazebo to ROS |

### Sensor topics

The bridge also maps these Gazebo sensor streams to ROS:

- `scan` to `sensor_msgs/msg/LaserScan`.
- `imu` to `sensor_msgs/msg/Imu`.
- `realsense/image` to `sensor_msgs/msg/Image`.
- `realsense/depth_image` to `sensor_msgs/msg/Image`.
- `realsense/points` to `sensor_msgs/msg/PointCloud2`.
- RGB and camera-info topics for `front_camera`, `rear_camera`, `left_camera`, and `right_camera`.

Inspect the active interfaces after launching:

```bash
ros2 topic list
ros2 topic echo /odom
ros2 topic hz /scan
ros2 topic info /cmd_vel
```

## Driving the vehicle

The Gazebo Ackermann steering plugin receives `geometry_msgs/msg/Twist` on `/cmd_vel`:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.1}}"
```

To stop the vehicle:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

The steering plugin uses the rear wheel joints for drive and the front steering joints for steering. It publishes odometry using `odom` as the parent frame and `base_footprint` as the child frame.

## Launch files

| File | Description |
| --- | --- |
| `launch/sim.launch.py` | Gazebo simulation, robot state publisher, RViz, spawning, and topic bridge. |
| `launch/GUI_sim.launch.py` | Same simulation workflow with the joint-state GUI enabled. |

## Package layout

```text
ackermann26_vehicle_gazebo/
  CMakeLists.txt
  package.xml
  README.md
  config/
    ros_bridge.yaml
  launch/
    GUI_sim.launch.py
    sim.launch.py
  worlds/
    vehicle_world.sdf
```

## Troubleshooting

### The vehicle does not spawn

Confirm that the description package has been built and sourced, then verify that `robot_state_publisher` is publishing `/robot_description`:

```bash
ros2 param get /robot_state_publisher robot_description
```

Also confirm that the requested world exists in `worlds/`.

### Gazebo topics are not visible in ROS

Check that `ros_gz_bridge` is running and inspect `config/ros_bridge.yaml`. Compare the Gazebo-side topic names with the names configured in the bridge. The bridge uses explicit ROS and Gazebo message types.

### RViz shows no model

Confirm that RViz is using `/robot_description` and that its fixed frame is a frame in the published TF tree, such as `base_footprint` or `odom`.

## License

This package declares the Apache-2.0 license. See `LICENSE` for the license text.
