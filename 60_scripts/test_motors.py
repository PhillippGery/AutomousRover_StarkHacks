#!/usr/bin/env python3
"""
test_motors.py — Quick motor test without ROS2.
Opens both ESP32 serial ports, spins all four motors at 100, then stops.
Run: python3 test_motors.py
"""

import serial
import time
import threading

FRONT_PORT = '/dev/ttyUSB0'
REAR_PORT  = '/dev/ttyUSB1'
BAUD       = 115200
TIMEOUT    = 1.0

responses = []
stop_read  = threading.Event()


def reader(ser: serial.Serial, label: str):
    while not stop_read.is_set():
        try:
            line = ser.readline()
            if line:
                text = line.decode(errors='replace').strip()
                msg  = f'[{label}] {text}'
                responses.append(msg)
                print(msg)
        except serial.SerialException:
            break


def main():
    print(f'Opening {FRONT_PORT} and {REAR_PORT} at {BAUD} baud...')

    try:
        ser_front = serial.Serial(FRONT_PORT, BAUD, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f'ERROR opening {FRONT_PORT}: {e}')
        ser_front = None

    try:
        ser_rear = serial.Serial(REAR_PORT, BAUD, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f'ERROR opening {REAR_PORT}: {e}')
        ser_rear = None

    # Start background reader threads
    threads = []
    if ser_front:
        t = threading.Thread(target=reader, args=(ser_front, 'FRONT'), daemon=True)
        t.start(); threads.append(t)
    if ser_rear:
        t = threading.Thread(target=reader, args=(ser_rear, 'REAR'), daemon=True)
        t.start(); threads.append(t)

    # Give boards time to boot
    time.sleep(1.0)

    print('\n--- Sending M1:100 M2:100 to both boards ---')
    if ser_front:
        ser_front.write(b'M1:100 M2:100\n')
    if ser_rear:
        ser_rear.write(b'M1:100 M2:100\n')

    time.sleep(2.0)

    print('\n--- Sending M1:0 M2:0 (STOP) to both boards ---')
    if ser_front:
        ser_front.write(b'M1:0 M2:0\n')
    if ser_rear:
        ser_rear.write(b'M1:0 M2:0\n')

    time.sleep(0.5)

    stop_read.set()

    if ser_front:
        ser_front.close()
    if ser_rear:
        ser_rear.close()

    print(f'\n--- Done. {len(responses)} total lines received ---')


if __name__ == '__main__':
    main()
