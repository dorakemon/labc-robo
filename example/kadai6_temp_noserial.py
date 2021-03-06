# import serial_lib as ser
import numpy as np, cv2, time, sys
from asciimatics.screen import ManagedScreen
from math import sin, cos, radians

pixel_value_str = ""
framePT = None
framePTHSV = None

def main():
    global framePT, framePTHSV
    # change following default values depending on calibration results
    MOTOR_DEFAULT_L = 122
    MOTOR_DEFAULT_R = 134
    SERVO_DEFAULT_V = 90
    SERVO_DEFAULT_H = 99
    # MOTOR_DEFAULT_L = 128
    # MOTOR_DEFAULT_R = 128
    # SERVO_DEFAULT_V = 90
    # SERVO_DEFAULT_H = 90

    # l = 128
    # r = 128
    # v = 73
    # h = 90
    l = 128
    r = 128
    v = 72
    h = 90

    # ser.motor_on(MOTOR_DEFAULT_L, MOTOR_DEFAULT_R)
    # ser.motor_stop()
    # ser.camera_on(SERVO_DEFAULT_V,SERVO_DEFAULT_H)
    # ser.camera_vertical(72)
    # ser.camera_horizontal(90)

    # Prepare perspective transformation matrix
    src_pnt = np.float32([[181.0, 199.0], [110.5, 199.0],
                        [104.7, 240.0], [184.2, 240.0]])
    dst_pnt = np.float32([[132.5, 240.0], [107.5, 240.0],
                        [107.5, 260.0], [132.5, 260.0]])
    map_matrix = cv2.getPerspectiveTransform(src_pnt, dst_pnt)

    # Camera number can be given as a command line argument
    # Note that camera number may change by rebooting or re-connection!
    # cap = cv2.VideoCapture(cv2.CAP_DSHOW+2 if len(sys.argv) == 1 else int(sys.argv[1]))
    cap = cv2.VideoCapture(702 if len(sys.argv) == 1 else int(sys.argv[1]))

    # only for windows user:
    #   when the above VideoCapture takes too long, comment the above line and uncomment both the below line and "cap.release()" line below the while loop
    # cap = cv2.VideoCapture((2 + cv2.CAP_DSHOW if len(sys.argv) == 1 else int(sys.argv[1])) + cv2.CAP_DSHOW) 

    # Set frame size; for Logicool C270n, allowed values include
    # 640x480, 320x240 and 160x120.  
    # High-resolution images require more processing cost.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    # Prepare a window for the original image
    cv2.namedWindow('src', cv2.WINDOW_NORMAL)
    cv2.moveWindow('src', 120,0)
    cv2.resizeWindow('src',320,240)

    # Another window for the transformed image
    cv2.namedWindow('dst', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('dst', mouse_event)
    cv2.moveWindow('dst', 460,0)
    cv2.resizeWindow('dst', 240,270)

    # Yetnother window for the mask image
    cv2.namedWindow('mask', cv2.WINDOW_NORMAL)
    cv2.moveWindow('mask', 720,0)
    cv2.resizeWindow('mask', 240,270)

    with ManagedScreen() as s:
        while True:
            _, frame = cap.read()
            _, frame = cap.read()
            _, frame = cap.read()
            _, frame = cap.read()
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            framePT = cv2.warpPerspective(frame, map_matrix, (240,270))
            framePTHSV = cv2.cvtColor(framePT, cv2.COLOR_BGR2HSV)

            # Pick the region whose H(ue) value is within the ranges
            # Reddish colors may have H values close either to 0 or 180,
            # so we compose two masks below
            # Green and blue have H values close to 60 and 120, respectively
            mask1 = cv2.inRange(framePTHSV, (0,100,100), (15,255,255))
            mask2 = cv2.inRange(framePTHSV, (170,100,100), (180,255,255))
            mask = mask1 + mask2

            # Find contours from the binary image
            # Result is an array of contour info; see OpenCV manual for details
            contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                                cv2.CHAIN_APPROX_SIMPLE)
            # Compute sizes (areas) of the contours found
            areas = [cv2.contourArea(c) for c in contours]

            # Draw the largest contour (if any) in blue and
            # enlosing rectangles (oblique and horizontal) in yellow and green
            if len(areas) > 0:
                getLargestContour(contours, areas, framePT, s)


        ### edit 
        ### frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ### # (2)?????????????????????????????????????????????????????????????????????????????????????????????
        ### frameGray = cv2.GaussianBlur(frameGray, (11,11), 0)
        ### # (3)????????????????????????????????????????????????????????????
        ### h, w = frameGray.shape
        ### circles = cv2.HoughCircles(frameGray, cv2.HOUGH_GRADIENT, 
        ###         dp=1, minDist=3, param1=20, param2=70, minRadius=30, maxRadius=max(h,w))
        ### if circles is not None:
        ###     circles = circles.squeeze(axis=0)
        ###     for i in range(0, min(3, len(circles))):
        ###         p = circles[i]
        ###         cv2.circle(frame, (int(p[0]),int(p[1])), 4, (0,255,0), -1, 8, 0)
        ###         cv2.circle(frame, (int(p[0]),int(p[1])), int(p[2]), (0,0,255), 6-2*i, 8, 0)

            # mainly edit here for Task 6
            # in thid template, robot goes straight if the largest area is positive value
            if np.max(areas, initial=0) > 0:
                l,r = move(100)
            ### elif circles is not None and len(circles) > 3:
            ###     l = 138
            ###     r = 138
            ###     time.sleep(0.3)
            else:
                l,r = stop()

            # ser.motor(l, r)

            # Display the resulting frames
            cv2.imshow('src', frame)
            cv2.imshow('dst', framePT)
            cv2.imshow('mask', mask)

            # Press 'q' in the frame window to exit loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # When everything done, release the capture
    #cap.release()
    #cv2.destroyAllWindows()
def stop():
    return 128,128

def move(pixel):
    l = r = 138
    # time.sleep(100)
    return l,r

def rotate(dir):
    if dir == 0: return 138, 128
    else: return 128,138
    
def back():
    return 118,118


# Draw rectangles and Print those information
 
def getLargestContour(contours, areas, framePT, s):
    #getLargestContour(contours, areas, framePT)
    max_index = np.argmax(areas)
    c = contours[max_index]
    cv2.drawContours(framePT, [c], 0, (255,0,0), 2)

    top_oblique = cv2.minAreaRect(c)        # ???????????????????????? ...
    top_oblique_x = int(top_oblique[0][0])  #   ?????? x ??????
    top_oblique_y = int(top_oblique[0][1])  #   ?????? y ??????
    top_oblique_w = int(top_oblique[1][0])  #   ???
    top_oblique_h = int(top_oblique[1][1])  #   ??????
    top_oblique_angle = int(top_oblique[2]) #   ?????????
    top_oblique_area = top_oblique_w * top_oblique_h  # ??????
    top_oblique_contour = np.int0(cv2.boxPoints(top_oblique))
    cv2.drawContours(framePT, [top_oblique_contour], 0, (0,255,255), 2)

    x,y,w,h = cv2.boundingRect(c)           # ???????????????????????????
    top_horizontal = np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h]])
    cv2.drawContours(framePT, [top_horizontal], 0, (0,255,0), 2)

    # my edit
    cv2.circle(framePT, (top_oblique_x,top_oblique_y), 4, (255,100,100), -1, 8, 0)
    # ???????????????????????????????????? 
    left_top = top_oblique_contour[0]
    right_top = top_oblique_contour[1]
    right_bottom = top_oblique_contour[2]
    left_bottom = top_oblique_contour[3]

    line1 = np.linalg.norm(right_bottom-left_bottom)
    line2 = np.linalg.norm(left_top-left_bottom)
    bottom_center = np.array([10,10])
    if line1 > line2:
        bottom_center = np.int0(1/2*(right_bottom-left_bottom)+left_bottom)
    elif line2 > line1:
        bottom_center = np.int0(np.absolute(1/2*(left_top-left_bottom)+left_bottom))
    cv2.circle(framePT, left_top, 1, (0,0,100), -1, 8, 0)
    cv2.circle(framePT, right_top, 3, (100,0,0), -1, 8, 0)
    cv2.circle(framePT, right_bottom, 3, (100,0,0), -1, 8, 0)
    cv2.circle(framePT, left_bottom, 3, (0,100,100), -1, 8, 0)
    cv2.circle(framePT, bottom_center, 10, (0,256,0), -1, 8, 0)




    s.print_at(f"Yellow contour:",0,0);
    s.print_at(f"center : ({top_oblique_x:3}, {top_oblique_y:3})", 2,1);
    s.print_at(f"width  :{top_oblique_w:6}", 2,2);
    s.print_at(f"height :{top_oblique_h:6}", 2,3);
    s.print_at(f"angle  :{top_oblique_angle:6}", 2,4);
    s.print_at(f"area   :{top_oblique_area:6}", 2,5);
    s.print_at(f"Green contour:", 0,6);
    s.print_at(f"width  :{w:6}", 2,7);
    s.print_at(f"height :{h:6}", 2,8);
    s.print_at(f"area   :{w * h:6}", 2,9);
    # s.print_at(pixel_value_str, 0, 11)
    s.print_at(f"MY EDIT:", 0,10);
    s.print_at(f"top_oblique_contour   :{top_oblique_contour}", 2,11);
    s.print_at(f"line1   :{line1:6}", 2,12);
    s.print_at(pixel_value_str, 0, 15)
    s.refresh()
    # time.sleep(0.1)

# Print the HSV value of the pixel just clicked

def mouse_event(event, x, y, _, __):
    global pixel_value_str
    if event == cv2.EVENT_LBUTTONUP:
        b,g,r = framePT[y,x]
        h,s,v = framePTHSV[y,x]
        pixel_value_str = f"({x:3},{y:3}) -> RGB=({r:3},{g:3},{b:3}) HSV=({h:3},{s:3},{v:3})"

if __name__ == '__main__':
    main()