import serial_lib as ser
import time
from enum import Enum, auto
from asciimatics.screen import ManagedScreen
from asciimatics.event import KeyboardEvent

SERVO_DEFAULT_V = 90
SERVO_DEFAULT_H = 90
current_v = 90
# current_h = 90
current_h = 99

class Servo_operation(Enum):
    v_inc = auto()
    v_dec = auto()
    h_inc = auto()
    h_dec = auto()

def s_swing(so):
    global current_v, current_h
    if so == Servo_operation.v_inc:
        current_v += 1
        ser.camera_vertical(current_v)
    elif so == Servo_operation.v_dec:
        current_v -= 1
        ser.camera_vertical(current_v)
    elif so == Servo_operation.h_inc:
        current_h += 1
        ser.camera_horizontal(current_h)
    else: 
        current_h -= 1
        ser.camera_horizontal(current_h)

ser.camera_on(SERVO_DEFAULT_V, SERVO_DEFAULT_H)
ser.camera_vertical(current_v)
ser.camera_horizontal(current_h)

with ManagedScreen() as s:
    s.print_at("Adjust orientation by   h / Leftarrow", 0, 0)
    s.print_at("                     or j / Downarrow", 0, 1)
    s.print_at("                     or k / Uparrow", 0, 2)
    s.print_at("                     or l / Rightarrow.", 0, 3)
    s.print_at("Press q to quit.", 0, 4)
    s.refresh()    

    loop = True
    while loop:
        e = s.get_event()
        if isinstance(e, KeyboardEvent):
            c = e.key_code
            if c == ord('k') or c == s.KEY_UP:
                s_swing(Servo_operation.v_inc)
            elif c == ord('j') or c == s.KEY_DOWN:
                s_swing(Servo_operation.v_dec)
            elif c == ord('h') or c == s.KEY_LEFT:
                s_swing(Servo_operation.h_dec)
            elif c == ord('l') or c == s.KEY_RIGHT:
                s_swing(Servo_operation.h_inc)
            elif c == ord('q'):
                loop = False
            s.print_at(f"V = {current_v:3}  H = {current_h:3}", 0, 6)
            s.refresh()

ser.close()
