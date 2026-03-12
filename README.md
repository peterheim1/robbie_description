# robbie_description

ROS2 Jazzy URDF and ros2_control hardware configuration for **Robbie** — a 4-wheel
swerve-drive home robot with dual 6-DOF arms, a pan/tilt head, a SCARA lift arm,
and multiple sensors.

---

## Package Contents

```
robbie_description/
├── urdf/
│   ├── robbie.urdf.xacro            ← Full robot model (dual 6-DOF arms + head)
│   ├── robbie_scara.urdf.xacro      ← SCARA arm variant (j0–j4 + gripper)
│   ├── scara_arm_ros2_control.xacro ← ros2_control hardware blocks (stepper + servos)
│   ├── robbie_ros2_control.xacro    ← Legacy ros2_control block (Feetech only)
│   └── mantis_gripper.xacro         ← Mantis gripper geometry
├── config/
│   ├── scara_controllers.yaml       ← Controller config for SCARA arm
│   └── controllers.yaml             ← Controller config for dual-arm robot
└── meshes/                          ← STL meshes for all robot links
```

---

## Robot Overview

| Feature | Detail |
|---|---|
| **Base** | 4-wheel swerve drive (omnidirectional), `base_link` / `base_footprint` |
| **Drive** | DDSM115 brushless hub motors × 4 via RS485 |
| **Steering** | ESP32 + 4× AS5600 magnetic encoders via I2C mux |
| **Height** | ~1.2 m (base 0.07 m + torso at 0.93 m) |
| **Lidar** | RPLidar at `scanner_link` (0.32 m height) |
| **Rear camera** | Intel RealSense D435 at `rear_camera_link` (rear-facing, docking) |
| **Front camera** | OAK-D Lite at `oak` link (head-mounted, forward-facing) |

---

## URDF Models

### `robbie.urdf.xacro` — Full dual-arm robot

Used in the main bringup. Includes:

- **Base** + torso at `xyz="0 0 0.93"` from base
- **Head**: `head_pan_joint` (yaw, ±90°) → `head_tilt_joint` (pitch, ±90°) → `head_box`
  - OAK-D camera attached to `head_box`
- **Left arm** (`left_` prefix): 6 revolute joints + gripper
- **Right arm** (`right_` prefix): 6 revolute joints + gripper
- ros2_control via `robbie_ros2_control.xacro` (Feetech only)

**Arm joint layout (per side):**

| Joint | Type | Axis | Limits |
|---|---|---|---|
| `{side}_joint_0` | Revolute | Y (shoulder pitch) | −90° to +86° |
| `{side}_joint_1` | Revolute | X (shoulder yaw) | ±17° (L) / ±90° (R) |
| `{side}_joint_2` | Revolute | Z (shoulder roll) | ±170° |
| `{side}_joint_3` | Revolute | Y (elbow pitch) | ±103° |
| `{side}_joint_4` | Revolute | X (wrist yaw) | ±90° |
| `{side}_joint_5` | Revolute | Y (wrist pitch) | ±90° |
| `{side}_joint_6` | Continuous | Y (wrist roll) | ±170° |
| `{side}_gripper` | Revolute | Z | −15° to +90° |

### `robbie_scara.urdf.xacro` — SCARA arm variant

Used with `servo_ros_2Control_launch.py`. Includes:

- Same base, torso, head, sensors as `robbie.urdf.xacro`
- **SCARA arm** with joints j0–j4 + gripper (single arm, centre-mounted)
- ros2_control via `scara_arm_ros2_control.xacro` (stepper + Feetech blocks)
- Includes `mantis_gripper.xacro` for end effector geometry

---

## ros2_control Hardware (`scara_arm_ros2_control.xacro`)

Two separate hardware blocks. Pass `use_mock_hardware:=true` to use
`mock_components/GenericSystem` instead of real hardware (simulation/testing).

### Block 1: `{name}_j0` — Prismatic lift (stepper)

| Item | Value |
|---|---|
| Plugin | `stepper_ros2_driver/StepperHardwareInterface` |
| Port | `/dev/stepper` |
| Joint | `j0` (prismatic, position + velocity state) |

### Block 2: `{name}_servos` — All Feetech joints

All Feetech servos share a **single** hardware block because LibSerial locks
`/dev/st_servo` exclusively — only one `FeetechHardwareInterface` instance can
own the port at a time.

| Plugin | `feetech_ros2_driver/FeetechHardwareInterface` |
|---|---|
| Port | `/dev/st_servo` |

**Servo ID map:**

| Joint | ID | Gear ratio | Notes |
|---|---|---|---|
| `j1` | 9 | 2.0 | SCARA shoulder |
| `j2` | 8 | 2.0 | SCARA elbow |
| `j3` | 19 | 1.0 | SCARA wrist |
| `j4` | 17 | 1.0 | SCARA wrist 2 |
| `gripper` | 18 | 1.0 | Initial pos −1.3 rad |
| `head_pan_joint` | 4 | 2.0 | Direction −1 |
| `head_tilt_joint` | 5 | 2.0 | Direction −1 |

---

## Controllers (`config/scara_controllers.yaml`)

| Controller | Type | Joints |
|---|---|---|
| `joint_state_broadcaster` | JointStateBroadcaster | all |
| `scara_arm_controller` | JointTrajectoryController | j0, j1, j2, j3, j4 |
| `scara_gripper_controller` | GripperActionController | gripper |
| `head_controller` | JointTrajectoryController | head_pan_joint, head_tilt_joint |

Update rate: **50 Hz**

---

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select robbie_description
source install/setup.bash
```

Dependencies: `feetech_ros2_driver`, `stepper_ros2_driver` (both in `~/ros2_ws/src/`)

---

## Launch

The URDF is loaded by `robbie_bot` launch files, not launched directly from this package.

```bash
# Full robot bringup (uses robbie.urdf.xacro)
ros2 launch robbie_bot base_driver.launch.py

# SCARA arm ros2_control (uses robbie_scara.urdf.xacro)
ros2 launch robbie_bot servo_ros_2Control_launch.py

# With mock hardware (no real servos/stepper needed)
ros2 launch robbie_bot servo_ros_2Control_launch.py use_mock_hardware:=true
```

---

## Verify URDF

```bash
# Check URDF parses without errors
ros2 run xacro xacro urdf/robbie_scara.urdf.xacro use_mock_hardware:=true | \
  ros2 run urdf_parser_py check_urdf.py

# Inspect loaded hardware after launch
ros2 control list_hardware_components
ros2 control list_controllers
ros2 topic echo /joint_states
```

---

## Device Symlinks Required

| Symlink | Device | Used by |
|---|---|---|
| `/dev/st_servo` | Feetech servo bus | `FeetechHardwareInterface` |
| `/dev/stepper` | ESP32 TMC2208 stepper | `StepperHardwareInterface` |
