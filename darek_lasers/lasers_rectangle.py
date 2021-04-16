import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    low_green = np.array([25, 52, 72])
    high_green = np.array([102, 255, 255])
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange (hsv, low_green, high_green)
    greencnts = cv2.findContours(mask.copy(),
                              cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_SIMPLE)[-2]

    if len(greencnts)>0:
        green_area = max(greencnts, key=cv2.contourArea)
        (xg,yg,wg,hg) = cv2.boundingRect(green_area)
        green_detect = cv2.rectangle(frame,(xg,yg),(xg+wg, yg+hg),(0,255,0),2)
    #     try:
    #         green_detect.any()
    #     except:
    #         pass
    # if green_detect.any():
    #     print("detected")

    cv2.imshow('frame',frame)
    cv2.imshow('HSV', hsv)
    cv2.imshow('mask',mask)

    k = cv2.waitKey(5)
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()