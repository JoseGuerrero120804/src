# Ackermann 26 Vehicle Simulation

ROS 2 description and Gazebo Sim integration for a small Ackermann-steering vehicle. The workspace contains the robot model, sensor definitions, RViz configuration, a Gazebo world, and a ROS-Gazebo bridge configuration.

## Packages

| Package | Purpose |
| --- | --- |
| `ackermann26_vehicle_description` | Xacro robot description, inertial properties, Gazebo sensor and steering plugins, RViz configurations, and display launch file. |
| `ackermann26_vehicle_gazebo` | Gazebo Sim launch files, bridge configuration, and the enclosed vehicle-world SDF. |

The active model entry point is `ackermann26_vehicle_description/urdf/mobile_robot.urdf.xacro`. `Backup2.urdf.xacro` is retained as a backup and is not used by the launch files.

## Requirements

- Linux with a sourced ROS 2 installation
- `colcon`
- `xacro`
- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- Gazebo Sim and the ROS-Gazebo integration packages `ros_gz_sim` and `ros_gz_bridge`

The exact ROS 2 distribution is not encoded in this repository. Use a distribution that provides the installed `ros_gz_*` packages and the Gazebo Sim Ackermann steering, sensor, IMU, and joint-state systems used by the model.

## Build

The repository directory is the workspace `src` directory. Build from its parent:

```bash
cd /home/nombre_usuario/Workspaces/sm26_ws
source /opt/ros/<ros2-distribution>/setup.bash
colcon build --symlink-install
source install/setup.bash
```

To build only these packages:

```bash
colcon build --symlink-install \
  --packages-select ackermann26_vehicle_description ackermann26_vehicle_gazebo
source install/setup.bash
```

## Run the model in RViz

This starts `robot_state_publisher`, `joint_state_publisher_gui`, and RViz with `Final_config.rviz`:

```bash
ros2 launch ackermann26_vehicle_description display.launch.py
```

Use the joint-state GUI to move the steering and wheel joints. The model publishes its robot description on `/robot_description` and its TF tree through `robot_state_publisher`.

## Run Gazebo Sim

The standard simulation launch starts Gazebo Sim, publishes the robot description, spawns the vehicle, starts RViz, and loads the configured ROS-Gazebo bridge:

```bash
ros2 launch ackermann26_vehicle_gazebo sim.launch.py
```

To also start the joint-state GUI:

```bash
ros2 launch ackermann26_vehicle_gazebo GUI_sim.launch.py
```

Both simulation launch files accept these arguments:

| Argument | Default | Description |
| --- | --- | --- |
| `world` | `vehicle_world.sdf` | World file name in `ackermann26_vehicle_gazebo/worlds/`. |
| `use_sim_time` | `true` | Use the Gazebo clock for ROS nodes. |
| `x` | `0.0` | Initial vehicle X position in metres. |
| `y` | `0.0` | Initial vehicle Y position in metres. |
| `z` | `0.0` | Initial vehicle Z position in metres. |
| `yaw` | `0.0` | Initial vehicle yaw in radians. |

Example:

```bash
ros2 launch ackermann26_vehicle_gazebo sim.launch.py \
  x:=0.5 y:=0.0 z:=0.05 yaw:=1.5708
```

The default `vehicle_world.sdf` contains a 4.0 m by 2.6 m rectangular track with 0.4 m high walls and a 100 m by 100 m ground plane. The walls are intended to be visible to the simulated lidar.

## Driving the vehicle

The Gazebo Ackermann steering plugin consumes `geometry_msgs/msg/Twist` on `cmd_vel`. For example:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.1}}"
```

Stop the vehicle by publishing zero velocity:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

The plugin uses the rear wheel joints for drive, the front steering joints for steering, and publishes odometry with `odom` as the parent frame and `base_footprint` as the child frame.

## ROS and Gazebo interfaces

The bridge configuration is in `ackermann26_vehicle_gazebo/config/ros_bridge.yaml`.

### Control and state

| ROS topic | Type | Direction |
| --- | --- | --- |
| `cmd_vel` | `geometry_msgs/msg/Twist` | ROS to Gazebo |
| `odom` | `nav_msgs/msg/Odometry` | Gazebo to ROS |
| `joint_states` | `sensor_msgs/msg/JointState` | Gazebo to ROS |
| `clock` | `rosgraph_msgs/msg/Clock` | Gazebo to ROS |

### Sensors

| ROS topic | Type | Rate / model detail |
| --- | --- | --- |
| `scan` | `sensor_msgs/msg/LaserScan` | 10 Hz GPU lidar, 720 samples, 0.12 m to 22.0 m |
| `imu` | `sensor_msgs/msg/Imu` | 100 Hz IMU |
| `front_camera/image_raw` | `sensor_msgs/msg/Image` | 30 Hz, 640 x 480 |
| `rear_camera/image_raw` | `sensor_msgs/msg/Image` | 30 Hz, 640 x 480 |
| `left_camera/image_raw` | `sensor_msgs/msg/Image` | 30 Hz, 640 x 480 |
| `right_camera/image_raw` | `sensor_msgs/msg/Image` | 30 Hz, 640 x 480 |
| `realsense/image` | `sensor_msgs/msg/Image` | RGB-D camera, 1280 x 720 |
| `realsense/depth_image` | `sensor_msgs/msg/Image` | RGB-D depth stream |
| `realsense/points` | `sensor_msgs/msg/PointCloud2` | RGB-D point cloud |
| `*/camera_info` | `sensor_msgs/msg/CameraInfo` | Camera calibration metadata |

The four CSI camera frames are `front_csi`, `rear_csi`, `left_csi`, and `right_csi`. Other sensor frames are `realsense_rear`, `lidar`, and `IMU`.

Inspect the live graph and topic names with:

```bash
ros2 topic list
ros2 topic echo /odom
ros2 topic hz /scan
ros2 topic info /cmd_vel
```

## Robot model

The model is built from primitive collision and visual geometry and includes:

- `base_footprint` and `base_link`
- Four continuous wheel joints
- Two revolute front steering joints limited to approximately +/-30 degrees
- Front and rear axle links
- Four CSI camera links
- A rear RGB-D camera link
- An IMU link
- A lidar link

Selected dimensions in `vehicle_properties.xacro` are:

| Property | Value |
| --- | ---: |
| Chassis length | 0.256 m |
| Chassis width | 0.148 m |
| Chassis height | 0.022 m |
| Wheel radius | 0.033 m |
| Wheel width | 0.022 m |
| Chassis mass | 1.0 kg |

The Gazebo Ackermann plugin is configured with a 0.25 m wheel base, 0.17 m wheel separation, 0.033 m wheel radius, 0.5 rad steering limit, and 50 Hz odometry publishing.

## Repository layout

```text
ackermann26_vehicle_description/
  launch/display.launch.py          RViz-only visualization
  urdf/mobile_robot.urdf.xacro      Active model entry point
  urdf/common_properties.xacro      Materials and inertia macros
  urdf/vehicle_properties.xacro     Dimensions and reusable link macros
  urdf/mobile_robot_gazebo.xacro    Gazebo plugins and sensors
  urdf/Backup2.urdf.xacro           Backup model
  rviz/Final_config.rviz             Active RViz configuration

ackermann26_vehicle_gazebo/
  launch/sim.launch.py               Gazebo simulation
  launch/GUI_sim.launch.py           Simulation plus joint GUI
  config/ros_bridge.yaml             ROS-Gazebo topic bridges
  worlds/vehicle_world.sdf           Default enclosed test world
```

## Validate the model

After sourcing the workspace, expand the active Xacro directly:

```bash
ros2 run xacro xacro \
  install/ackermann26_vehicle_description/share/ackermann26_vehicle_description/urdf/mobile_robot.urdf.xacro \
  > /tmp/ackermann26_vehicle.urdf
```

For a quick runtime check, start the simulation and verify that `/robot_description`, `/clock`, `/odom`, `/joint_states`, and `/scan` appear:

```bash
ros2 topic list
```

If a sensor topic is missing, check Gazebo Sim plugin availability, the bridge entries in `ros_bridge.yaml`, and the Gazebo-side topic names before changing the ROS topic name.

## Troubleshooting

### Package or launch file not found

Build from `/home/nombre_usuario/Workspaces/sm26_ws`, then source both the ROS 2 installation and `install/setup.bash` in the same terminal.

### Gazebo opens but the vehicle does not spawn

Check that `robot_state_publisher` is running and that `/robot_description` contains a valid expanded URDF:

```bash
ros2 param get /robot_state_publisher robot_description
```

Also confirm that the selected world exists under `ackermann26_vehicle_gazebo/worlds/`.

### RViz shows no model

Set RViz's fixed frame to a frame in the published TF tree, typically `base_footprint` or `odom`, and confirm that the RobotModel display uses `/robot_description`.

### Topics exist in Gazebo but not ROS

Compare Gazebo and ROS topic names, then inspect `ackermann26_vehicle_gazebo/config/ros_bridge.yaml`. The bridge uses explicit Gazebo message types, so the installed Gazebo Sim version must provide compatible message and system plugin names.

## License

The packages declare the Apache-2.0 license. See the `LICENSE` file in each package for the applicable license text.
