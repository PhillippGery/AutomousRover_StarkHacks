# Wiring Reference

> **Note:** Pin assignments below are the planned design. Finalize against the physical build at the hackathon before flashing firmware.

## Arduino Mega → L298N Motor Driver Connections

```
Arduino Mega    L298N #1 (FL + BL)    L298N #2 (FR + BR)
Pin 2  ──────── IN1 (FL forward)
Pin 3  ──────── IN2 (FL reverse)
Pin 4  ──────── ENA (FL PWM)
Pin 5  ──────── IN1 (BL forward)
Pin 6  ──────── IN2 (BL reverse)
Pin 7  ──────── ENB (BL PWM)
Pin 8  ─────────────────────────── IN1 (FR forward)
Pin 9  ─────────────────────────── IN2 (FR reverse)
Pin 10 ─────────────────────────── ENA (FR PWM)
Pin 11 ─────────────────────────── IN1 (BR forward)
Pin 12 ─────────────────────────── IN2 (BR reverse)
Pin 13 ─────────────────────────── ENB (BR PWM)
```

All L298N GND pins connect to Arduino GND and battery negative.
L298N +12V pins connect to 12V motor rail.
L298N +5V (logic) pins connect to 5V rail (or use Arduino 5V if current allows).

## Encoder Connections

Use interrupt-capable pins on the Mega (2, 3, 18, 19, 20, 21):

| Motor | Channel A Pin | Channel B Pin |
|-------|--------------|--------------|
| FL | 18 | 19 |
| FR | 20 | 21 |
| BL | 2 | 3 |
| BR | — | — (extend if needed) |

> **Warning:** Pins 20 and 21 are shared with I2C (SDA/SCL). If MPU-6050 is on I2C, reassign FR encoder channels to other interrupt pins or use a software encoder library.

## I2C Bus — MPU-6050

| Signal | Arduino Mega Pin |
|--------|----------------|
| SDA | Pin 20 |
| SCL | Pin 21 |
| VCC | 3.3V |
| GND | GND |
| AD0 | GND (address 0x68) |
| INT | Pin 2 (optional interrupt) |

## Serial — MiniPC ↔ Arduino

Connect Arduino Mega USB-B port to AMD MiniPC USB-A/USB-C port.
Device will appear as `/dev/ttyUSB0` or `/dev/ttyACM0` on Ubuntu — check with `ls /dev/tty*` after connection.

## Sensor Bus Summary

| Sensor | Interface | Arduino/RPi Pin |
|--------|----------|----------------|
| MPU-6050 | I2C | Pins 20 (SDA), 21 (SCL) |
| HC-SR04 ×4 | Digital (trig/echo) | Pins 22–29 (TBD) |
| MG90S servos | PWM | Pins 44–47 (TBD) |
| RealSense T265 | USB 3.0 | MiniPC USB directly |
| Scanse Sweep | USB-Serial | MiniPC `/dev/ttyUSB0` |
