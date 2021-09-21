import cv2, sys

# Camera number can be given as a command line argument
# Note that camera number may change by rebooting or re-connection!
cap1 = cv2.VideoCapture(2 if len(sys.argv) == 1 else int(sys.argv[1]))
cap2 = cv2.VideoCapture(4 if len(sys.argv) == 1 else int(sys.argv[2]))

# Set frame size; for Logicool C270n, possible values include
# 640x480, 320x240 and 160x120.  
# High-resolution images require more processing cost.
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 320);
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 320);
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);

# Create a named window so that properties (e.g., window position)
# can be specified later
cv2.namedWindow('webcam1', cv2.WINDOW_NORMAL)
cv2.moveWindow('webcam1', 80, 0)
cv2.resizeWindow('webcam1', 320, 240)

cv2.namedWindow('webcam2', cv2.WINDOW_NORMAL)
cv2.moveWindow('webcam2', 440, 0)
cv2.resizeWindow('webcam2', 320, 240)

while True:
    # Capture frame-by-frame; the first return value is not used
    _, frame1 = cap1.read()
    _, frame2 = cap2.read()

    # Operations on the frame come here
    # Note that the frame is in the BGR (not RGB) format!
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    # cv2.imshow('webcam', gray)
    cv2.imshow('webcam1', frame1)
    cv2.imshow('webcam2', frame2)

    # Press 'q' in the frame window to exit loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything has been done, release the capture
cap1.release()
cap2.release()
cv2.destroyAllWindows()
