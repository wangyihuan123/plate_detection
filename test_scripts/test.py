import time
# import cv2

# cv2.namedWindow("display")
# while True:
#     k = cv2.waitKey(1)
#
#     # Mask out all but the equivalent ASCII key code in the low byte
#     k = k & 0xFF
#     if (k != 255):
#         print(k)
#     # time.sleep(1)

# mydict = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
# for k, v in mydict.items():
#     if v == 3:
#         del mydict[k]
# print(mydict)

import pathlib
print(pathlib.Path.cwd())