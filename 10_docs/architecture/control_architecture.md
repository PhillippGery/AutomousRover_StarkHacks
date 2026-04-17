# Motor Control Architecture

## ROS2 ↔ Arduino Responsibility Split

GUARDIAN splits motor control across two processors to keep each layer focused:

| Layer | Owns | Detail |
|-------|------|--------|
| **ROS2 (MiniPC)** | High-level motion | Subscribes `/cmd_vel` Twist → computes 4× wheel RPM targets via mecanum kinematics → sends over USB serial |
| **Arduino Mega** | Low-level control | Receives RPM targets → runs independent PID per wheel → outputs PWM to L298N H-bridges → reads encoder feedback |

This split allows Nav2 and teleop to reason in velocity space while the Arduino handles real-time closed-loop control at its own rate.

## Mecanum Kinematics

Given a desired robot velocity `(vx, vy, omega)` and chassis geometry `(L = half wheel-base length, W = half wheel-base width)`:

```
FL_rpm = (vx - vy - (L+W) * omega) / wheel_radius
FR_rpm = (vx + vy + (L+W) * omega) / wheel_radius
BL_rpm = (vx + vy - (L+W) * omega) / wheel_radius
BR_rpm = (vx - vy + (L+W) * omega) / wheel_radius
```

Where:
- `vx` = forward velocity (m/s)
- `vy` = lateral/strafe velocity (m/s)
- `omega` = yaw rate (rad/s)
- `wheel_radius` = 0.048 m (JGB37-3530 + mecanum wheel)

> **Key demo:** Strafing (`vy ≠ 0, vx = 0, omega = 0`) is the signature omnidirectional move — all four wheels spin simultaneously in opposing directions to translate sideways with no rotation.

## Serial Protocol

Communication between MiniPC and Arduino uses plain-text newline-delimited messages at 115200 baud.

**MiniPC → Arduino (RPM targets):**
```
FL:150 FR:150 BL:-150 BR:-150\n
```

**Arduino → MiniPC (encoder feedback):**
```
ENC:FL:148 FR:151 BL:-149 BR:-152\n
```

Values are signed integers representing target/measured RPM. Negative = reverse.

## PID Per Wheel

Each wheel has an independent PID controller on the Arduino:

```
error = target_rpm - measured_rpm
output = Kp * error + Ki * integral + Kd * derivative
PWM = clamp(output, -255, 255)
```

Starting gains (tune at hackathon):
- `Kp = 1.5`
- `Ki = 0.0`
- `Kd = 0.1`
