import cv2
from PIL import Image

from util import get_limits


red = [0, 0, 255]  # yellow in BGR colorspace
yellow = [0, 255, 255]
blue = [255,0,0]
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()

    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lowerLimit_yellow, upperLimit_yellow = get_limits(color=yellow)
    lowerLimit_red, upperLimit_red = get_limits(color=red)
    lowerLimit_blue, upperLimit_blue = get_limits(color=blue)
    mask_yellow = cv2.inRange(hsvImage, lowerLimit_yellow, upperLimit_yellow)
    mask_red = cv2.inRange(hsvImage,lowerLimit_red, upperLimit_red)
    #mask_blue = cv2.inRange(hsvImage,)

    res_yellow = cv2.bitwise_and(frame, frame, mask=mask_yellow)
    res_red = cv2.bitwise_and(frame, frame, mask=mask_red)
    combined = cv2.add(res_red,res_yellow)


    mask_ = Image.fromarray(res_yellow)
    #mask_red = Image.fromarray(mask_red)

    bbox = mask_.getbbox()

    if bbox is not None:
        x1, y1, x2, y2 = bbox

        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)


    cv2.imshow('frame', combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()