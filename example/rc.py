import serial_lib as ser
import time
from enum import Enum, auto
from asciimatics.screen import ManagedScreen
from asciimatics.event import KeyboardEvent

MOTOR_DEFAULT_L = 125
MOTOR_DEFAULT_R = 131
SERVO_DEFAULT_V = 89
SERVO_DEFAULT_H = 88
STEP = 12

l = 128
r = 128
v = 73
h = 90

class Motor_operation(Enum):
    inc = auto()
    dec = auto()
    left = auto()
    right = auto()

class Servo_operation(Enum):
    v_inc = auto()
    v_dec = auto()
    h_inc = auto()
    h_dec = auto()

def change_speed(so):
    global l, r
    if so == Motor_operation.inc:
        l -= STEP
        r -= STEP
    elif so == Motor_operation.dec:
        l += STEP
        r += STEP
    elif so == Motor_operation.left:
        l += STEP
        r -= STEP
    else: # so == Motor_operation.right
        l -= STEP
        r += STEP
    ser.motor(l, r)

def s_swing(so):
    global v, h
    if so == Servo_operation.v_inc:
        v += 1
        ser.camera_vertical(v)
    elif so == Servo_operation.v_dec:
        v -= 1
        ser.camera_vertical(v)
    elif so == Servo_operation.h_inc:
        h += 1
        ser.camera_horizontal(h)
    else: 
        h -= 1
        ser.camera_horizontal(h)

ser.motor_on(MOTOR_DEFAULT_L, MOTOR_DEFAULT_R)
ser.motor_stop()
ser.camera_on(SERVO_DEFAULT_V,SERVO_DEFAULT_H)
ser.camera_vertical(72)
ser.camera_horizontal(90)

with ManagedScreen() as s:
    s.print_at("Control speed/turn by arrow keys", 0, 0)
    s.print_at("and servo orientaion by h/j/k/l keys.", 0, 1)
    s.print_at("Press q to quit.", 0, 2)
    s.refresh()    

    loop = True
    while loop:
        e = s.get_event()
        if isinstance(e, KeyboardEvent):
            c = e.key_code
            if c == s.KEY_UP:
                change_speed(Motor_operation.inc)
            elif c == s.KEY_DOWN:
                change_speed(Motor_operation.dec)
            elif c == s.KEY_LEFT:
                change_speed(Motor_operation.left)
            elif c == s.KEY_RIGHT:
                change_speed(Motor_operation.right)
            elif c == ord('z'):
                l = 128 + STEP
                r = 128 + STEP
                change_speed(Motor_operation.inc)
            elif c == ord('k'):
                s_swing(Servo_operation.v_inc)
            elif c == ord('j'):
                s_swing(Servo_operation.v_dec)
            elif c == ord('h'):
                s_swing(Servo_operation.h_inc)
            elif c == ord('l'):
                s_swing(Servo_operation.h_dec)
            elif c == ord('q'):
                loop = False
            s.print_at
            s.print_at(f"L = {l:3}  R = {r:3}", 0, 4)
            s.print_at(f"V = {v:3}  H = {h:3}", 0, 5)
            s.refresh()

ser.close()
