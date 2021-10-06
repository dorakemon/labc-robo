import numpy as np, cv2, sys, time
from asciimatics.screen import ManagedScreen

from parameter import *
from enums import Mode
from state import Search, FindPart, AngleAdjust, Search2
from image_processing import *
import controller as con
import serial_lib as ser
from batch import Batch

pixel_value_str = ""

framePT = None
framePTHSV = None

current_status = Mode.SEARCH
previous_status = Mode.SEARCH
# 何本倒したか
finished_count = 0

def main():
    global framePT, framePTHSV
    global current_status, previous_status, finished_count
    se_s = Search()
    se2_s = Search2()
    fp_s = FindPart()
    aa_s = AngleAdjust()

    ser.motor_on(MOTOR_DEFAULT_L, MOTOR_DEFAULT_R)
    ser.motor_stop()
    ser.camera_on(SERVO_DEFAULT_V,SERVO_DEFAULT_H)
    ser.camera_vertical(74)
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
            # 円認識の時は80°に調整
            if current_status == Mode.ANGLE_ADJUST or current_status == Mode.CHECK_CENTER:
                ser.camera_vertical(80)
                circles = getHoughCircles(frame)
                len_circles, circle_x, len_cir_iqr = calcCirclesCenter(circles,frame)
                bt.update(len_circles=len_circles, circle_x=circle_x, len_circles_iqr=len_cir_iqr)
            else: ser.camera_vertical(74)
            # endregion

            bt.print()
            cv2.imshow('src', frame)
            cv2.imshow('dst', framePT)

            if init_cam_count < 5: 
                init_cam_count += 1
            else: 
                # 移動系
                if current_status == Mode.SEARCH:
                    # 紙を発見時
                    if paper_area > MIN_PART_AREA:
                        if se_s.lookingRight():
                            con.rotate(bt, 30)
                        elif se_s.lookingLeft():
                            con.rotate(bt, -30)
                        se_s.reset()
                        current_status = Mode.FIND_PARTIAL
                    else: 
                        se_s.update()
                        if se_s.move_forward:
                            con.move_sec(bt, SEARCH_MOVE_FORWARD_SEC)
                    init_cam_count = 0
                    time.sleep(1)

                if current_status == Mode.SEARCH2:
                    # 紙を発見時
                    if paper_area > MIN_PART_AREA:
                        if se2_s.lookingRight():
                            con.rotate(bt, 30)
                        elif se2_s.lookingLeft():
                            con.rotate(bt, -30)
                        se2_s.reset()
                        current_status = Mode.FIND_PARTIAL
                    else: 
                        se2_s.update()
                        if se2_s.do_rotate:
                            con.rotate(bt, 90)
                        if se2_s.move_forward:
                            con.move_sec(bt, se2_s.move_ratio * SEARCH2_MOVE_FORWARD_SEC)
                    init_cam_count = 0
                    time.sleep(1)
                
                elif current_status == Mode.FIND_PARTIAL:
                    if MIN_FULL_AREA <= paper_area <= MAX_FULL_AREA:
                        if fp_s.lookingRight(): 
                            con.rotate(bt, 10)
                        elif fp_s.lookingLeft(): 
                            con.rotate(bt, -10)
                        fp_s.reset()
                        current_status = Mode.FIND_ALL
                    elif paper_area > MAX_FULL_AREA:
                        bt.print_error("TOO BIG PAPER FOUND")
                    else: # 一部分見つかっている状態
                        fp_s.update()
                        if fp_s.move_forward:
                            con.move_sec(bt, FINDPART_MOVE_FORWARD_SEC)
                    init_cam_count = 0
                    time.sleep(1)

                elif current_status == Mode.FIND_ALL:
                    # 直進 -> 回転 -> 移動 -> 回転
                    con.move_sec(bt, INIT_MOVE_TIME)
                    con.rotate(bt, camera_angle)
                    con.move(bt, d_close_camera)
                    con.rotate(bt, close_angle)
                    current_status = Mode.ANGLE_ADJUST
                
                # ここは必ず円が角度45-135の間に見つかると仮定
                elif current_status == Mode.ANGLE_ADJUST:
                    # 確認: 円映っているかの判定条件
                    if len_circles > 2:
                        if aa_s.lookingRight():
                            con.rotate(bt, +20)
                        elif aa_s.lookingLeft():
                            con.rotate(bt, -20)
                        aa_s.reset()
                        current_status = Mode.CHECK_CENTER
                    else:
                        aa_s.update()
                    init_cam_count = 0
                    time.sleep(1)
                
                # 必ず円が画面の中に近くある状態で、微調整
                elif current_status == Mode.CHECK_CENTER:
                    # 確認： ハフ変換ののための中心座標
                    frame_center = int(frame.shape[1] / 2 ) - 40
                    if frame_center - ADJUST_ALLOW_PIXEL <= circle_x <= frame_center + ADJUST_ALLOW_PIXEL:
                        current_status = Mode.APPROACH
                    elif frame_center + ADJUST_ALLOW_PIXEL < circle_x:
                        con.rotate(bt, +ADJUST_ANGLE)
                        init_cam_count = 0
                        time.sleep(1)
                    elif circle_x < frame_center - ADJUST_ALLOW_PIXEL:
                        con.rotate(bt, -ADJUST_ANGLE)
                        init_cam_count = 0
                        time.sleep(1)

                elif current_status == Mode.APPROACH:
                    con.move_sec(bt, APPROACH_MOVE_SEC)
                    finished_count += 1
                    current_status = Mode.SEARCH2
                    con.back(bt, sec=SEARCH2_BACK_SEC)
                    # con.reverse(bt)
                
                bt.update(finished_count=finished_count, current_status=current_status, 
                    se_state=se_s.state, fp_state=fp_s.state, aa_state=aa_s.state, 
                    move_record=con.MOVE_RECORD)
                bt.print_state()

                # バッファしてしまっている画像を読み捨てる
                for i in range(5):
                    _, frame = cap.read()

                if finished_count >= 3:
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