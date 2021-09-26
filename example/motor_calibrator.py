import serial_lib as ser
import time
from enum import Enum, auto
from asciimatics.screen import ManagedScreen
from asciimatics.event import KeyboardEvent

MOTOR_DEFAULT_L = 128
MOTOR_DEFAULT_R = 128
current_l = 128
current_r = 128

class Motor_operation(Enum):
    l_inc = auto()
    l_dec = auto()
    r_inc = auto()
    r_dec = auto()

def s_swing(so):
    global current_l, current_r
    if so == Motor_operation.l_inc:
        current_l += 1
    elif so == Motor_operation.l_dec:
        current_l -= 1
    elif so == Motor_operation.r_inc:
        current_r += 1
    else: # so == Motor_operation.r_dec
        current_r -= 1
    ser.motor(current_l, current_r)

ser.motor_on(128, 128)
ser.motor_stop()

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
                s_swing(Motor_operation.r_inc)
            elif c == ord('j') or c == s.KEY_DOWN:
                s_swing(Motor_operation.r_dec)
            elif c == ord('h') or c == s.KEY_LEFT:
                s_swing(Motor_operation.l_inc)
            elif c == ord('l') or c == s.KEY_RIGHT:
                s_swing(Motor_operation.l_dec)
            elif c == ord('q'):
                loop = False
            s.print_at(f"L = {current_l:3}  R = {current_r:3}", 0, 6)
            s.refresh()

ser.close()
