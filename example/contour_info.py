import numpy as np, cv2, time, sys
from asciimatics.screen import ManagedScreen

pixel_value_str = ""

# Print the HSV value of the pixel just clicked
def mouse_event(event, x, y, _, __):
    global pixel_value_str
    if event == cv2.EVENT_LBUTTONUP:
        b,g,r = framePT[y,x]
        h,s,v = framePTHSV[y,x]
        pixel_value_str = f"({x:3},{y:3}) -> RGB=({r:3},{g:3},{b:3}) HSV=({h:3},{s:3},{v:3})"

# Prepare perspective transformation matrix
src_pnt = np.float32([[181.0, 199.0], [110.5, 199.0],
                      [104.7, 240.0], [184.2, 240.0]])
dst_pnt = np.float32([[132.5, 240.0], [107.5, 240.0],
                      [107.5, 260.0], [132.5, 260.0]])
map_matrix = cv2.getPerspectiveTransform(src_pnt, dst_pnt)

# Camera number can be given as a command line argument
# Note that camera number may change by rebooting or re-connection!
cap = cv2.VideoCapture(cv2.CAP_DSHOW+1 if len(sys.argv) == 1 else int(sys.argv[1]))

# cap = cv2.VideoCapture(2 if len(sys.argv) == 1 else int(sys.argv[1]))

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
            max_index = np.argmax(areas)
            c = contours[max_index]
            cv2.drawContours(framePT, [c], 0, (255,0,0), 2)

            top_oblique = cv2.minAreaRect(c)        # 最小包囲長方形の ...
            top_oblique_x = int(top_oblique[0][0])  #   中心 x 座標
            top_oblique_y = int(top_oblique[0][1])  #   中心 y 座標
            top_oblique_w = int(top_oblique[1][0])  #   幅
            top_oblique_h = int(top_oblique[1][1])  #   高さ
            top_oblique_angle = int(top_oblique[2]) #   傾き角
            top_oblique_area = top_oblique_w * top_oblique_h  # 面積
            top_oblique_contour = np.int0(cv2.boxPoints(top_oblique))
            cv2.drawContours(framePT, [top_oblique_contour], 0, (0,255,255), 2)

            x,y,w,h = cv2.boundingRect(c)           # 水平最小包囲長方形
            top_horizontal = np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h]])
            cv2.drawContours(framePT, [top_horizontal], 0, (0,255,0), 2)

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
            s.print_at(pixel_value_str, 0, 11)
            s.refresh()
            # time.sleep(0.1)

        # Display the resulting frames
        cv2.imshow('src', frame)
        cv2.imshow('dst', framePT)
        cv2.imshow('mask', mask)

        # Press 'q' in the frame window to exit loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
