import numpy as np, cv2, sys, time
from asciimatics.screen import ManagedScreen

from parameter import *
from enums import AA_STATE, FIND_PART, FP_STATE, SE_STATE, Mode
from image_processing import *
import controller as con
import serial_lib as ser
from batch import Batch

pixel_value_str = ""

framePT = None
framePTHSV = None

# edit later
current_status = Mode.SEARCH
previous_status = Mode.SEARCH
se_state = SE_STATE.S_FRONT
aa_state = AA_STATE.INIT
# 何本倒したか
finished_count = 0

def main():
    global framePT, framePTHSV
    global current_status, previous_status, se_state, aa_state, finished_count
    fp_s = FIND_PART()

    ser.motor_on(MOTOR_DEFAULT_L, MOTOR_DEFAULT_R)
    ser.motor_stop()
    ser.camera_on(SERVO_DEFAULT_V,SERVO_DEFAULT_H)
    ser.camera_vertical(73)
    ser.camera_horizontal(90)

    # region CV2-SETTINGS
    # Prepare perspective transformation matrix
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
    cv2.setMouseCallback('dst', mouse_event)
    cv2.moveWindow('dst', 460,0)
    cv2.resizeWindow('dst', 240,270)
    # endregion

    # 初めに複数回画像処理を行ってから動作を開始
    # 確認: もしバッファに
    init_cam_count = 0

    with ManagedScreen() as s:
        while True:
            bt = Batch(s)
            bt.print_color(pixel_value_str)
            bt.print_error("                 ")
            # region 画像の前処理
            _, frame = cap.read()
            framePT = cv2.warpPerspective(frame, map_matrix, (240,270))
            framePTHSV = cv2.cvtColor(framePT, cv2.COLOR_BGR2HSV)
            # endregion

            # 画像処理系
            # region 色紙認識系の処置
            # 確認: 色紙のマスクのHSVの閾値に問題はないか
            mask = getMask(COLOR_ORDER[finished_count], framePTHSV)
                
            contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            areas = [cv2.contourArea(c) for c in contours]
            paper_area = 0
            if len(areas) > 0:
                top_oblique = getLargestContour(contours, areas)
                oblique_contour = np.int0(cv2.boxPoints(top_oblique))
                paper_area = top_oblique[1][0] * top_oblique[1][1]
                cv2.drawContours(framePT, [oblique_contour], 0, (0,255,255), 2)
                center_point,opposit_point,slope = getNearestLongLine(oblique_contour, framePT)
                close_point = getBisectorPoint(center_point, opposit_point, slope, framePT)
                camera_angle,close_angle = getAngle(center_point, close_point)
                d_close_camera,d_center_close = getDistance(center_point, close_point)
                bt.update(top_oblique=top_oblique, slope=slope, close_point=close_point, 
                    angle0=camera_angle, angle1=close_angle,
                    d_close_camera=d_close_camera, d_center_close=d_center_close)
            # endregion

            # region ハフ変換関係の処理
            # 修正: close pointに近づいたときに何度にすればよいか
            # 修正: カメラの角度を戻す
            if current_status == Mode.ANGLE_ADJUST or current_status == Mode.CHECK_CENTER:
                ser.camera_vertical(80)
                # ser.camera_horizontal(90)
                circles = getHoughCircles(frame)
                len_circles, circle_x, len_cir_iqr = calcCirclesCenter(circles,frame)
                bt.update(len_circles=len_circles, circle_x=circle_x, len_circles_iqr=len_cir_iqr)
            else: ser.camera_vertical(73)
            # endregion

            bt.print()
            cv2.imshow('src', frame)
            cv2.imshow('dst', framePT)

            if init_cam_count < 5: 
                init_cam_count += 1
            else: 
                # 移動系
                # bt.update(finished_count=finished_count, current_status=current_status, 
                #     se_state=se_state, fp_state=fp_s.state, aa_state=aa_state, 
                #     move_record=con.MOVE_RECORD)
                # 
                if current_status == Mode.SEARCH:
                    # 紙を発見時
                    if paper_area > MIN_PART_AREA:
                        ser.camera_horizontal(90)
                        if se_state == SE_STATE.S_RIGHT:
                            con.rotate(bt, 30)
                        elif se_state == SE_STATE.S_LEFT:
                            con.rotate(bt, -30)
                        se_state = SE_STATE.S_FRONT
                        current_status = Mode.FIND_PARTIAL
                        init_cam_count = 0
                        time.sleep(1)
                    
                    elif se_state == SE_STATE.S_FRONT:
                        ser.camera_horizontal(120)
                        init_cam_count = 0
                        time.sleep(1)
                        se_state = SE_STATE.S_RIGHT
                    elif se_state == SE_STATE.S_RIGHT:
                        ser.camera_horizontal(60)
                        init_cam_count = 0
                        time.sleep(1)
                        se_state = SE_STATE.S_LEFT
                    elif se_state == SE_STATE.S_LEFT:
                        se_state = SE_STATE.S_FRONT
                        ser.camera_horizontal(90)
                        init_cam_count = 0
                        time.sleep(1)
                        con.move_sec(bt, SEARCH_MOVE_FORWARD_SEC)
                
                elif current_status == Mode.FIND_PARTIAL:
                    # 確認: このリバース悪さするかも
                    if paper_area < MIN_PART_AREA:
                        current_status = Mode.SEARCH
                        # con.reverse(bt)
                        fp_s.reset()
                    elif MIN_FULL_AREA <= paper_area <= MAX_FULL_AREA:
                        current_status = Mode.FIND_ALL
                        if fp_s == FP_STATE.S_RIGHT: con.rotate(45)
                        elif fp_s == FP_STATE.S_LEFT: con.rotate(-45)
                        """ ser.camera_horizontal(90) """
                        fp_s.reset()
                    elif paper_area > MAX_FULL_AREA:
                        # too big paper
                        bt.print_error("TOO BIG PAPER FOUND")
                    else: # 一部分見つかっている状態
                        if fp_s.state == FP_STATE.INIT:
                            fp_s.update(FP_STATE.S_FRONT)
                        elif fp_s.state == FP_STATE.S_FRONT:
                            """ ser.camera_horizontal(135) """
                            fp_s.update(FP_STATE.S_RIGHT)
                        elif fp_s.state == FP_STATE.S_RIGHT:
                            """ ser.camera_horizontal(45) """
                            fp_s.update(FP_STATE.S_LEFT)
                        elif fp_s.state == FP_STATE.S_LEFT and not fp_s.moved_1sec:
                            """ ser.camera_horizontal(90) """
                            fp_s.move_forward()
                            con.move_sec(bt, 1)
                            fp_s.update(FP_STATE.S_FRONT)
                        elif fp_s.state == FP_STATE.S_LEFT and fp_s.moved_1sec:
                            # go back to search
                            #  reverse(bt)
                            # 
                            # 修正
                            # 
                            # current_status = Mode.SEARCH
                            fp_s.moved_1sec = False
                            fp_s.update(FP_STATE.INIT)

                elif current_status == Mode.FIND_ALL:
                    # 直進 -> 回転 -> 移動 -> 回転
                    con.move_sec(bt, INIT_MOVE_TIME)
                    con.rotate(bt, camera_angle)
                    con.move(bt, d_close_camera)
                    con.rotate(bt, close_angle)
                    current_status = Mode.ANGLE_ADJUST
                
                # ここは必ず円が角度45-135の間に見つかると仮定
                # 誤差が多ければカウントでループを抜けて、reverse()->SEARCHがいいかも
                elif current_status == Mode.ANGLE_ADJUST:
                    # 確認: 円映っているかの判定条件
                    if len_circles > 2:
                        if aa_state == AA_STATE.S_RIGHT:
                            con.rotate(bt, +20)
                        elif aa_state == AA_STATE.S_LEFT:
                            con.rotate(bt, -20)
                        aa_state == AA_STATE.INIT
                        ser.camera_horizontal(90)
                        current_status = Mode.CHECK_CENTER
                        init_cam_count = 0
                        time.sleep(1)
                    elif aa_state == AA_STATE.INIT:
                        # 修正: カメラが円を認識できる縦の角度に修正
                        aa_state = AA_STATE.S_FRONT
                    elif aa_state == AA_STATE.S_FRONT:
                        ser.camera_horizontal(110)
                        time.sleep(1)
                        init_cam_count = 0
                        aa_state = AA_STATE.S_RIGHT
                    elif aa_state == AA_STATE.S_RIGHT:
                        ser.camera_horizontal(70) 
                        time.sleep(1)
                        init_cam_count = 0
                        aa_state = AA_STATE.S_LEFT
                    elif aa_state == AA_STATE.S_LEFT:
                        ser.camera_horizontal(90) 
                        time.sleep(1)
                        init_cam_count = 0
                        aa_state = AA_STATE.INIT
                
                # 必ず円が画面の中に近くある状態で、微調整
                elif current_status == Mode.CHECK_CENTER:
                    # 修正： ハフhennkannのための中心座標s
                    frame_center = int(frame.shape[1] / 2 ) - 40
                    if frame_center - ADJUST_ALLOW_PIXEL <= circle_x <= frame_center + ADJUST_ALLOW_PIXEL:
                        aa_state = AA_STATE.INIT
                        current_status = Mode.APPROACH
                    elif frame_center + ADJUST_ALLOW_PIXEL < circle_x:
                        con.rotate(bt, +ADJUST_ANGLE)
                        init_cam_count = 0
                    elif circle_x < frame_center - ADJUST_ALLOW_PIXEL:
                        con.rotate(bt, -ADJUST_ANGLE)
                        init_cam_count = 0

                elif current_status == Mode.APPROACH:
                    if finished_count >= 3: break
                    con.move_sec(bt, APPROACH_MOVE_SEC)
                    finished_count += 1
                    current_status = Mode.SEARCH
                    con.reverse(bt)
                
                bt.update(finished_count=finished_count, current_status=current_status, 
                    se_state=se_state, fp_state=fp_s.state, aa_state=aa_state, 
                    move_record=con.MOVE_RECORD)
                bt.print_state()

                # バッファしてしまっている画像を読み捨てる
                for i in range(10):
                    _, frame = cap.read()

                if finished_count >= 3:
                    con.back(bt)
                    con.back(bt)
                    con.rotate(bt, 360)
                    break

            # Press 'q' in the frame window to exit loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

def mouse_event(event, x, y, _, __):
    global pixel_value_str
    if event == cv2.EVENT_LBUTTONUP:
        b,g,r = framePT[y,x]
        h,s,v = framePTHSV[y,x]
        pixel_value_str = f"({x:3},{y:3}) -> RGB=({r:3},{g:3},{b:3}) HSV=({h:3},{s:3},{v:3})"

if __name__ == '__main__':
    main()