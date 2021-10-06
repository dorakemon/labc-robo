import time

from parameter import MOVE_VELOCITY, ROTATE_SOCOND
from batch import Batch
"""import serial_lib as ser"""

MOVE_RECORD = []

def record(bt, action_type, sec):
    # もし種類がrotateで右回転なら正秒 左回転なら負秒
    # 直近の動作と同じ動作なら追加
    # じかんがあれば途中で色紙見つけたときの処理
    # global MOVE_RECORD
    if len(MOVE_RECORD) and MOVE_RECORD[-1]["type"] == action_type:
        MOVE_RECORD[-1]["sec"] += sec
    else: MOVE_RECORD.append({"type": action_type, "sec":sec})
    bt.update(move_record=MOVE_RECORD)
    bt.print_record()
    print(MOVE_RECORD)

def speed(l: int, r: int):
    return 128+l, 128+r

def pixel_to_sec(pixel:int) -> int:
    return pixel / MOVE_VELOCITY

def angle_to_sec(angle:int) -> int:
    return ROTATE_SOCOND / 360 * angle

def stop(bt: Batch):
    bt.update(status="stop", pixel=0, angle=0, time=0)
    bt.print_car_info()
    # これらのコメントはすべて解除
    """ser.motor(*speed(0, 0))"""

def move(bt: Batch, pixel, torque=20):
    sec = pixel_to_sec(pixel)
    record(bt, "move", sec)
    bt.update(status="move", pixel=pixel, angle=0, time=sec)
    bt.print_car_info()
    """ser.motor(*speed(torque, torque))"""
    # これらのコメントはすべて解除
    time.sleep(sec)
    stop(bt)

def move_sec(bt: Batch, sec, torque=20):
    record(bt, "move", sec)
    bt.update(status="move_sec", pixel=0, angle=0, time=sec)
    bt.print_car_info()
    """ser.motor(*speed(torque, torque))"""
    time.sleep(sec)
    stop(bt)

def rotate(bt: Batch, angle, pace=20):
    if angle > 0: 
        """ser.motor(*speed(+pace, -pace))"""
        sec = angle_to_sec(angle)
        record(bt, "rotate", sec)
    elif angle < 0: 
        """ser.motor(*speed(-pace, +pace))"""
        sec = angle_to_sec(-angle)
        record(bt, "rotate", -sec)
    bt.update(status="rotate", pixel=0, angle=angle, time=sec)
    bt.print_car_info()
    time.sleep(sec)
    stop(bt)
    
def back(bt: Batch, torque=20):
    record(bt, "back", 1)
    bt.update(status="back",  pixel=0, angle=0, time=1)
    bt.print_car_info()
    """ser.motor(*speed(-torque, -torque))"""
    time.sleep(1)
    stop(bt)

def reverse(bt: Batch):
    # 反対の動きをする
    # 確認: moveの反対がバックでもいいのか
    # いったん180度回転して正反対でもいいかも
    while len(MOVE_RECORD) != 0:
        record = MOVE_RECORD.pop()
        action = record["type"]
        sec = record["sec"]
        torque = 20
        pace = 20
        bt.update(status=f"rev_{action}", time=sec)
        bt.print_car_info()
        if action == "move":
            """ser.motor(*speed(-torque, -torque))"""
        elif action == "rotate":
            if sec > 0:
                """ser.motor(*speed(-pace, +pace))"""
            elif sec < 0:
                """ser.motor(*speed(+pace, -pace))"""
                sec = -sec
        elif action == "back":
            """ser.motor(*speed(+torque, +torque))"""
        bt.update(move_record=MOVE_RECORD)
        bt.print_record()
        time.sleep(sec)
    stop(bt)
