# Arduino Motor Controller

**Owner: Vedant**

This folder contains the Arduino Mega firmware for GUARDIAN's low-level motor control.

## Sketch

[guardian_motor_control/guardian_motor_control.ino](guardian_motor_control/guardian_motor_control.ino)

## Hardware

- Arduino Mega 2560
- 2× L298N H-bridge motor driver modules
- 4× JGB37-3530 12V DC encoder motors
- 4× Mecanum wheels

## Setup

See [10_docs/setup/arduino_setup.md](../../10_docs/setup/arduino_setup.md) for full setup instructions.

## Serial Protocol

| Direction | Format | Example |
|-----------|--------|---------|
| MiniPC → Arduino | `FL:<rpm> FR:<rpm> BL:<rpm> BR:<rpm>\n` | `FL:150 FR:150 BL:-150 BR:-150` |
| Arduino → MiniPC | `ENC:FL:<rpm> FR:<rpm> BL:<rpm> BR:<rpm>\n` | `ENC:FL:148 FR:151 BL:-149 BR:-152` |

Baud rate: 115200
