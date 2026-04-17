# Arduino Motor Controller Setup

## Requirements

- Arduino Mega 2560
- Arduino IDE 2.x (download from https://www.arduino.cc/en/software)
- USB-B cable

## Steps

### 1. Install Arduino IDE 2.x

Download and install Arduino IDE 2.x for your operating system.

### 2. Install Required Libraries

No third-party libraries are required — the sketch uses standard Arduino libraries only.

### 3. Open the Sketch

In Arduino IDE, open:

```
20_hardware/arduino/guardian_motor_control/guardian_motor_control.ino
```

### 4. Select Board

- Go to **Tools → Board → Arduino AVR Boards → Arduino Mega or Mega 2560**
- If not listed, install via **Tools → Board → Boards Manager** — search "Arduino AVR Boards"

### 5. Select COM Port

- Go to **Tools → Port** and select the port corresponding to the Arduino Mega
- On Linux: usually `/dev/ttyACM0` or `/dev/ttyUSB0`
- On Windows: `COM3`, `COM4`, etc.

### 6. Upload

Click **Upload** (→ arrow button). Wait for "Done uploading."

### 7. Verify

Open **Tools → Serial Monitor** and set baud rate to **115200**.

You should see the Arduino startup message. The Arduino is now waiting for RPM commands.

### 8. Test Motor Response

In the Serial Monitor, send:

```
FL:100 FR:100 BL:100 BR:100
```

All four wheels should spin forward at ~100 RPM. Verify direction matches the mecanum wheel orientation (check `10_docs/hardware/wiring_diagram.md`).

To stop:

```
FL:0 FR:0 BL:0 BR:0
```

> **Note:** Implement PID and encoder reading before this test will reflect actual RPM. The stub accepts the protocol but does not yet control motors. Fill in the TODOs in `guardian_motor_control.ino`.
