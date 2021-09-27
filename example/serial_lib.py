# Simple servo control library
import serial
import time
 
# Port name can be found in Arduino IDE (under Tools menu)
ser = serial.Serial('COM3', 115200, timeout=1)

time.sleep(2)  # wait for the establishment of communication

# モーター電源オン，静止パルス幅設定
# pwL, pwR は 左右モーターパルス幅調整値、中心は128
def motor_on(pwL, pwR):
    ser.write(bytes([255,11,0])) # モーター電源オンコマンド
    time.sleep(0.5)
    ser.write(bytes([255,13,256-pwL,256-pwR,0])) # モーター静止パルス幅設定コマンド
    time.sleep(0.05)

# モーター電源オフ（脱力）
# def motor_release():
#     ser.write(bytes([255,12,0]))
#     time.sleep(0.05)

# モーター駆動
# vl, vr: 128を中心とする速度（およそ 78〜178）
def motor(vl, vr):
    ser.write(bytes([255,14,256-vl,256-vr,0]))
    time.sleep(0.05)

# モーター停止（脱力はしない）
def motor_stop():
    motor(128,128)

# カメラサーボ電源オン，中心アングル設定
# thV, thH は真正面を向くための縦アングル値（90を中心に微調整）
def camera_on(thV, thH):
    ser.write(bytes([255,21,0]))  # カメラサーボ電源オンコマンド
    time.sleep(0.5)
    ser.write(bytes([255,23,thV,thH,0])) # カメラサーボ中心位置設定コマンド
    time.sleep(0.05)

# カメラサーボ電源オフ（脱力）
# def camera_release():
#     ser.write(bytes([255,22,0]))
#     time.sleep(0.5)

# カメラサーボ縦移動
# th は角度（30〜105、真正面は90）
def camera_vertical(th):
    ser.write(bytes([255,24,th,0]))
    time.sleep(0.05)

# カメラサーボ横移動
# th は角度（30〜150、真正面は90）
def camera_horizontal(th):
    ser.write(bytes([255,25,th,0]))
    time.sleep(0.05)

# LED点滅
# n は点滅回数
def LED_blink(n):
    ser.write(bytes([255,99,n,0]))
    time.sleep(0.05)              

def close():
    ser.close
    
