# ackermann26_vehicle_description

ROS 2 package containing the Ackermann vehicle robot description, reusable Xacro macros, Gazebo sensor/plugin definitions, and RViz configurations.

## Purpose

This package defines the complete `ackermann_vehicle` model used by the simulation. It provides:

- The active Xacro entry point for the vehicle.
- Visual, collision, inertial, and joint definitions.
- Ackermann steering and wheel-joint configuration.
- Four CSI camera links, one RGB-D camera, an IMU, and a lidar.
- Gazebo Sim plugins and sensor definitions included in the robot description.
- RViz configurations for inspecting the robot model and TF tree.

The active model is `urdf/mobile_robot.urdf.xacro`. `urdf/Backup2.urdf.xacro` is a retained backup and is not used by the launch files.

## Dependencies

The package declares these runtime dependencies:

- `xacro`
- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `ros_gz_sim`
- `ros_gz_bridge`

It uses the `ament_cmake` build system.

## Build

Build from the colcon workspace root, not from this package directory:

```bash
cd /home/nombre_usuario/Workspaces/sm26_ws
source /opt/ros/<ros2-distribution>/setup.bash
colcon build --symlink-install --packages-select ackermann26_vehicle_description
source install/setup.bash
```

## RViz visualization

Launch the model with `robot_state_publisher`, the joint-state GUI, and RViz:

```bash
ros2 launch ackermann26_vehicle_description display.launch.py
```

The launch file loads:

- `urdf/mobile_robot.urdf.xacro`
- `rviz/Final_config.rviz`

The robot description is published on `/robot_description`. The joint-state GUI can be used to inspect steering and wheel-joint motion. RViz is configured to display the robot model and TF frames.

## Robot model

The active Xacro defines these principal links and systems:

- `base_footprint` and `base_link`
- Front and rear axle links
- Four wheel links with continuous joints
- Front-left and front-right steering links with revolute joints
- Four CSI camera links: `front_csi`, `rear_csi`, `left_csi`, and `right_csi`
- RGB-D camera link: `realsense_rear`
- IMU link: `IMU`
- Lidar link: `lidar`

The front steering joints are limited to approximately plus or minus 30 degrees. The front wheel joints mimic the corresponding rear wheel joints.

Selected vehicle properties from `urdf/vehicle_properties.xacro`:

| Property | Value |
| --- | ---: |
| Chassis length | 0.256 m |
| Chassis width | 0.148 m |
| Chassis height | 0.022 m |
| Chassis mass | 1.0 kg |
| Wheel radius | 0.033 m |
| Wheel width | 0.022 m |

## Xacro files

| File | Description |
| --- | --- |
| `urdf/mobile_robot.urdf.xacro` | Active vehicle description and link/joint assembly. |
| `urdf/common_properties.xacro` | Materials and inertia macros for boxes, spheres, and cylinders. |
| `urdf/vehicle_properties.xacro` | Vehicle dimensions and reusable axle, camera, wheel, and steering macros. |
| `urdf/mobile_robot_gazebo.xacro` | Gazebo steering, sensor, joint-state, and simulation plugin configuration. |
| `urdf/Backup2.urdf.xacro` | Backup copy of an earlier model description. |

## Gazebo sensors in the model

The included Gazebo Xacro defines:

- Four RGB cameras at 640 x 480 and 30 Hz.
- One RGB-D camera at 1280 x 720 and 30 Hz.
- A GPU lidar at 10 Hz with 720 horizontal samples and a 0.12 m to 22.0 m range.
- An IMU at 100 Hz.
- The Gazebo Ackermann steering system.
- Gazebo sensor and joint-state publisher systems.

The Gazebo topic names and ROS bridge mappings are maintained in the separate `ackermann26_vehicle_gazebo` package.

## Validate the Xacro

Expand the active model directly from the source tree:

```bash
source /opt/ros/<ros2-distribution>/setup.bash
ros2 run xacro xacro \
  urdf/mobile_robot.urdf.xacro \
  > /tmp/ackermann26_vehicle.urdf
```

A successful command produces a plain URDF file that can be inspected or passed to other ROS tools.

## Package layout

```text
ackermann26_vehicle_description/
  CMakeLists.txt
  package.xml
  README.md
  launch/
    display.launch.py
  rviz/
    Ackermann_first_config.rviz
    Final_config.rviz
  urdf/
    Backup2.urdf.xacro
    common_properties.xacro
    mobile_robot.urdf.xacro
    mobile_robot_gazebo.xacro
    vehicle_properties.xacro
```

## License

This package declares the Apache-2.0 license. See `LICENSE` for the license text.
