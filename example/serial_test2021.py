# Simple servo swing program 
import serial_lib as ser
import time

ser.camera_on(90, 92)
ser.camera_vertical(80)
ser.camera_horizontal(90)
ser.motor_on(128, 128)
ser.motor_stop()
time.sleep(0.5)

for i in range(2):
    for k in range(5, 60, 3):
        ser.motor(128-k, 128-k)
        time.sleep(0.05)
    for k in range(60, 5, -3):
        ser.motor(128-k, 128-k)
        time.sleep(0.05)

ser.motor_stop()

ser.camera_horizontal(120)
time.sleep(0.5)
ser.camera_horizontal(60)
time.sleep(0.5)
ser.camera_horizontal(90)
ser.camera_vertical(73)

ser.close( )
