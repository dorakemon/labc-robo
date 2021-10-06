import numpy as np, cv2, sys, time
from asciimatics.screen import ManagedScreen

import controller as con
import serial_lib as ser
from parameter import *
from batch import Batch

framePT = None
framePTHSV = None

def main():
    global framePT, framePTHSV

    ser.motor_on(MOTOR_DEFAULT_L, MOTOR_DEFAULT_R)
    ser.motor_stop()
    ser.camera_on(SERVO_DEFAULT_V,SERVO_DEFAULT_H)
    ser.camera_on(SERVO_DEFAULT_V,SERVO_DEFAULT_H)
    ser.camera_vertical(72)
    ser.camera_horizontal(90)

    src_pnt = np.float32([[181.0, 199.0], [110.5, 199.0], [104.7, 240.0], [184.2, 240.0]])
    dst_pnt = np.float32([[132.5, 240.0], [107.5, 240.0], [107.5, 260.0], [132.5, 260.0]])
    map_matrix = cv2.getPerspectiveTransform(src_pnt, dst_pnt)

    cap = cv2.VideoCapture(cv2.CAP_DSHOW+2 if len(sys.argv) == 1 else int(sys.argv[1]))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cv2.namedWindow('src', cv2.WINDOW_NORMAL)
    cv2.moveWindow('src', 120,0)
    cv2.resizeWindow('src',320,240)
    cv2.namedWindow('dst', cv2.WINDOW_NORMAL)
    cv2.moveWindow('dst', 460,0)
    cv2.resizeWindow('dst', 240,270)

    with ManagedScreen() as s:
        bt = Batch(s)
        temp = 0
        while True:
            _, frame = cap.read()
            framePT = cv2.warpPerspective(frame, map_matrix, (240,270))
            framePTHSV = cv2.cvtColor(framePT, cv2.COLOR_BGR2HSV)
            if temp == 10:
                con.move_sec(bt, INIT_MOVE_TIME)
            cv2.imshow('src', frame)
            cv2.imshow('dst', framePT)
            temp += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # rotate 1
        # 以下を実行して、一周にかかる時間をパラメータをいじって 調整
        # con.rotate(bt, 360)
        # con.rotate(bt, -360)

        # rotate 2
        # 30度ずつ１２回小刻みに回転しても1周になるか
        # for i in range(12):
            # con.rotate(bt, 30)
            # con.rotate(bt, -30)
        
        # rotaete3  
        # con.rotate(bt, 180)
        # con.rotate(bt, 360)

        # init_move_time 1
        # 付箋を貼ってタイマーで計測
        # con.move(bt, 3)

        # init_move_time 2
        # 付箋の位置にぴったり重なるか
        con.move(bt, INIT_MOVE_TIME)

        # con.move 1
        # mainで、angle0, (angle1), d_close_cameraを取得
        # ２等分線状に乗るかどうか
        camera_angle = 120
        close_angle = 60
        d_close_camera = 100
        d_1 = 300
        # con.move_sec(bt, INIT_MOVE_TIME)
        # con.rotate(bt, angle0)
        # con.move(d_close_camera)
        # con.rotate(bt, angle1)

        # reverse() 確認
        # con.reverse(bt)

        # con.move_sec(bt, INIT_MOVE_TIME)
        # con.move_sec(bt, INIT_MOVE_TIME)
        # con.move_sec(bt, INIT_MOVE_TIME)

        # con.rotate(bt, camera_angle)
        # con.move(bt, 200)
        con.move(bt, 200)
        # con.move(bt, 200)
        con.back(bt)
        # con.move(bt, 100)
        # con.move(bt, d_close_camera)
        con.rotate(bt, close_angle)
        con.move(bt, d_1)
        con.rotate(bt, -100)
        # con.rotate(bt, 300)
        con.move(bt, d_1)
        con.move(bt, d_1)
        time.sleep(3)
        con.reverse(bt)

if __name__ == '__main__':
    main()