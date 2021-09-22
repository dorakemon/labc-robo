import cv2, sys

# Print the HSV value of the pixel just clicked
def mouse_event(event, x, y, _, __):
    if event == cv2.EVENT_LBUTTONUP:
        pixel_value = frameGray[y,x]
        print(f"({x:3},{y:3}) -> {pixel_value}")

# Camera number can be given as a command line argument
# Note that camera number may change by rebooting or re-connection!
cap = cv2.VideoCapture(cv2.CAP_DSHOW+2 if len(sys.argv) == 1 else int(sys.argv[1]))

# Set frame size; for Logicool C270n, allowed values include
# 640x480, 320x240 and 160x120.  
# High-resolution images require more processing cost.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320);
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);

# Prepare a window for the original image
cv2.namedWindow('src', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('src', mouse_event)
cv2.moveWindow('src', 120,0)
cv2.resizeWindow('src',320,240)

# Another window for the transformed image
cv2.namedWindow('circles', cv2.WINDOW_NORMAL)
cv2.moveWindow('circles', 460,0)
cv2.resizeWindow('circles', 320,240)

while True:
    # (1) カメラからの入力画像1フレームをframeに格納
    _, frame = cap.read()
    frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # (2)ハフ変換のための前処理（画像を平滑化しないと誤検出が出やすい）
    frameGray = cv2.GaussianBlur(frameGray, (11,11), 0)

    # (3)ハフ変換による円の検出と検出した円の描画
    h, w = frameGray.shape
    circles = cv2.HoughCircles(frameGray, cv2.HOUGH_GRADIENT, 
              dp=1, minDist=3, param1=20, param2=70, minRadius=10, maxRadius=max(h,w))
    if circles is not None:
        circles = circles.squeeze(axis=0)
        for i in range(0, min(3, len(circles))):
            p = circles[i]
            cv2.circle(frame, (int(p[0]),int(p[1])), 4, (0,255,0), -1, 8, 0)
            cv2.circle(frame, (int(p[0]),int(p[1])), int(p[2]), (0,0,255), 6-2*i, 8, 0)

    # (4) 検出結果表示用のウィンドウを確保し表示する
    cv2.imshow('circles', frame)
    cv2.imshow('src', frameGray)

    # Press 'q' in the frame window to exit loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cap.release()
# cv2.destroyAllWindows()
