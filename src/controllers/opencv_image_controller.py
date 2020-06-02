import cv2
import numpy as np
import math
import time
import logging
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import engine

from .threaded_engine_controller import ThreadedEngineController

WINDOW_NAME = "DISPLAY"

class OpencvImageController(ThreadedEngineController):
    target_box_colour = (0, 255, 255)

    def __init__(self):
        super(OpencvImageController, self).__init__()
        self._image_to_show = None
        self._plate_coordinates = []  # [pt1, pt2, pt3, pt4]
        self._vehicle_region = []  # [top_left_pt, bottom_right_tp]
        self._log = logging.getLogger()


    def notify_frame_data(self, frameData):
        image = frameData.getImage()
        # image = frameData.getDisplayImage()  # sometimes need original display image

        self._image_to_show = image
        jsonresult = frameData.getDetectionResult()
        vehicle_region = jsonresult["results"][0]["vehicle_region"]
        self._vehicle_region = [(vehicle_region["x"], vehicle_region["y"]),
                                (vehicle_region["x"] + vehicle_region["width"], vehicle_region["y"] + vehicle_region["height"])]

        # todo: display plate region as well

    def run(self):
        cv2.namedWindow(WINDOW_NAME)
        while not self._engine_shutdown:

            if self._image_to_show is not None:
                cv2.rectangle(self._image_to_show, self._vehicle_region[0], self._vehicle_region[1],
                              self.target_box_colour, 2)
                # todo: display plate region as well

                cv2.imshow(WINDOW_NAME, self._image_to_show)
                cv2.waitKey(100)

    def __del__(self):
        super(OpencvImageController, self).__del__()
        cv2.destroyAllWindows()
