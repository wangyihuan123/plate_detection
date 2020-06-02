import os, sys
import pathlib
import threading
import time as t
import queue
import cv2
from .frame_data import FrameData
import logging

# TEST_FRAMES = [300, 1200, 1800, 2200, 2700, 3000, 3600, 4000, 4500]
TEST_FRAMES = [1, 100, 4000, 4001, 4002, 4003, 4004]
# TEST_PLATES = ["WAX081", "XFG774", "1HG9TF", "WCW856", "ZPR916", "1FL2KF", "1JQ7RG","unknown", "AXZ074"]  # the last second is unknown


ROI_RATIO = 0.5

DEVICE_WAIT_TIMEOUT_SECONDS = 10

class FrameGrabber(object):

    FPS = 30

    def __init__(self, output_queue):
        super(FrameGrabber, self).__init__()

        self._output_queue = output_queue

        self._run_thread = False
        self._worker_thread = None

        self._running = False
        self._pipeline = None
        self._image_id = 0  # valid id start from 1
        self._cap = None
        self.frames_dir = str(pathlib.Path.cwd()) + "/../running_data/"
        self._log = logging.getLogger()


    def run(self):
        self._log.info("run frame_grabber")
        while self._running:

            # # only for testing
            # self._cap.set(cv2.CAP_PROP_POS_FRAMES, self._image_id-1)
            # self._image_id += 1
            # if self._image_id not in TEST_FRAMES:
            #     continue
            #
            # try:
            #     ret, frame = self._cap.read()
            # except RuntimeError as e:
            #     self._log.info(e)
            #     t.sleep(0.5)
            #     continue
            #
            # if ret is not True:
            #     self._log.info("Ending")
            #     self._log.info("{} frames in the test video".format(self._image_id))  # 4681 frames in all
            #     break


            # #############################
            self._image_id = 1200
            test_image = self.frames_dir + "frame_" + str(self._image_id) + ".png"
            frame = cv2.imread(test_image)

            if frame is None:
                self._log.info("image is None")
                self._log.info(self._image_id)
                continue

            if self._output_queue.full():
                try:
                    self._output_queue.get(block=False)
                except queue.Empty:
                    pass

            self._output_queue.put(
                FrameData(frame, self._image_id))


    def start(self):

        # 4681 frames in 157 seconds, around 30 fps
        TEST_VIDEO = "../test_data/Ardeer.mp4"
        if not os.path.exists(TEST_VIDEO):
            self._log.info("test video not exist")
            self._log.info(pathlib.Path(__file__).parent.absolute())
            self._log.info(pathlib.Path().absolute())
            return


        self._cap = cv2.VideoCapture(TEST_VIDEO)  # in all 157 seconds
        if not self._cap.isOpened():  # check if we succeeded
            self._log.info("open video fail...")
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self.run)
        self._worker_thread.start()

    def stop(self):

        if self._running:
            with self._output_queue.mutex:
                self._output_queue.queue.clear()
            self._running = False
            if self._worker_thread is not None:
                self._worker_thread.join()
                self._worker_thread = None


    def __del__(self):
        pass
