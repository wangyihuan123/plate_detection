import time
import cv2

cv2.namedWindow("display")
while True:
    k = cv2.waitKey(1)

    # Mask out all but the equivalent ASCII key code in the low byte
    k = k & 0xFF
    if (k != 255):
        print(k)
    # time.sleep(1)