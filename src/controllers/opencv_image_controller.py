import cv2
import numpy as np
import math
import time

# import geometry

import engine

from .threaded_engine_controller import ThreadedEngineController

WINDOW_NAME = "DISPLAY"

TEXT_MARGIN = 10
TEXT_ROW_1 = 20
TEXT_ROW_2 = 40
TEXT_ROW_3 = 60
TEXT_ROW_4 = 80
TEXT_ROW_5 = 100
TEXT_ROW_6 = 120
TEXT_ROW_7 = 140
TEXT_ROW_8 = 160
TEXT_ROW_9 = 180


COLOUR_BLUE = (255, 0, 0)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (0, 0, 255)
COLOUR_YELLOW = (0, 255, 255)
COLOUR_WHITE = (255, 255, 255)


COLOUR_GOOD = COLOUR_GREEN
COLOUR_BAD = COLOUR_RED


class OpencvImageController(ThreadedEngineController):

    def __init__(self):
        super(OpencvImageController, self).__init__()

        cv2.namedWindow(WINDOW_NAME)

        self._image_to_show = None

    def notify_state_update(self, state, status_txt=""):
        super(OpencvImageController, self).notify_state_update(state, status_txt)

        if state == engine.ApplicationEngine.CONTROLLER_STATE_IDLE:
            print("opencv display init as blank")
            cv2.imshow(WINDOW_NAME, np.zeros((100, 100, 3), np.uint8))

    def notify_frame_data(self, frameData):
        image = frameData.getImage()
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        print("notify_frame_data")
        self._image_to_show = image

    def run(self):
        print(self._engine_shutdown)
        while not self._engine_shutdown:

            if self._image_to_show is not None:
                cv2.imshow(WINDOW_NAME, self._image_to_show)
                self._image_to_show = None
                print("image is not none")
                k = cv2.waitKey(1)

    def __del__(self):
        super(OpencvImageController, self).__del__()
        cv2.destroyAllWindows()
