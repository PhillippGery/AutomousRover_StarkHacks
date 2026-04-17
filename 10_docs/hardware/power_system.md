# Power System Design

## Power Budget

| Component | Voltage | Est. Current | Notes |
|-----------|---------|-------------|-------|
| 4× JGB37-3530 motors | 12V | 1A each (4A total) | Stall up to 3A each — size fuses accordingly |
| Arduino Mega | 5V | 200mA | Powered via USB from MiniPC or buck converter |
| AMD MiniPC | 19V DC | ~3A | Separate supply recommended |
| SO-101 arms ×2 | 5V USB-C | 2A each | Powered from MiniPC USB-C ports |
| ESP32 ×3 | 3.3V | 250mA each | Via Arduino 3.3V pin or dedicated buck |
| Sensors / servos | 5V | 500mA total | Via 5V rail |

**Total estimated draw:** ~12A peak at 12V motor rail + ~7A at 5V logic rail

## Power Rail Diagram

```
[18650 4S Pack ~14.8V]
         │
    ┌────┴─────┐
    │          │
  [12V rail] [LM2596 Buck → 5V rail]
    │          │
  Motors    Arduino + Sensors + ESP32
```

> The AMD MiniPC and SO-101 arms should be powered from a separate supply (wall adapter or dedicated battery pack) to isolate motor switching noise from the compute platform.

## Safety Guidelines

- **Always fuse the motor rail** — add a 5A automotive blade fuse between the battery and the 12V motor rail.
- **Never power motors and logic from the same unregulated rail** — motor switching injects noise that can reset microcontrollers.
- **Do not exceed 3A continuous per L298N channel** — the L298N is rated at 2A continuous, 3A peak.
- **Disconnect battery when wiring** — the 18650 pack can deliver dangerous short-circuit current.
- **Check polarity before connecting** — reverse voltage will damage the L298N and Arduino immediately.

## Wiring Sequence (startup)

1. Connect logic power (5V rail, Arduino, sensors) first — verify with multimeter.
2. Connect MiniPC and arms via USB-C.
3. Connect motor power (12V rail) last — only after software is ready.
4. Emergency stop: disconnect 12V battery terminal.
