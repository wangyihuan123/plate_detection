import os, sys
import pathlib
import threading
import time as t
import queue
import cv2
import numpy
from .frame_data import FrameData

TEST_FRAMES = [300, 1200, 1800, 2200, 2700, 3000, 3600, 4000, 4500]
# TEST_PLATES = ["WAX081", "XFG774", "1HG9TF", "WCW856", "ZPR916", "1FL2KF", "1JQ7RG","unknown", "AXZ074"]  # the last second is unknown

ROI_RATIO = 0.5

DEVICE_WAIT_TIMEOUT_SECONDS = 10

class FrameGrabber(object):

    FPS = 30

    def __init__(self, output_queue, headless):
        super(FrameGrabber, self).__init__()

        self._headless = headless
        self._output_queue = output_queue

        self._run_thread = False
        self._worker_thread = None

        self._running = False
        self._selection = None
        self._roi = None
        self._pipeline = None
        self._config = None
        self._cap = None
        self._image_id = 0  # valid id start from 1

    def run(self):
        print("run frame_grabber")
        while self._running:
            try:
                ret, frame = self._cap.read()
            except RuntimeError as e:
                print(e)
                t.sleep(0.5)
                continue

            if ret is not True:
                print("Ending")
                print("{} frames in the test video".format(self._image_id))  # 4681 frames in all
                break

            self._image_id += 1

            # #############################33
            test_image = "/home/eva/code/rushdigital/running_data/frame_1200.png"
            frame = cv2.imread(test_image)
            if frame is None:
                print("image is None")
                print(self._image_id)
                continue

            # only for testing
            # if self._image_id not in TEST_FRAMES:
            #     continue

            if self._output_queue.full():
                try:
                    self._output_queue.get(block=False)
                except queue.Empty:
                    pass

            # print(self._image_id,  frame.shape)
            self._output_queue.put(
                FrameData(frame, self._image_id, self._headless))

    def start(self):
        print("start frame_grabber")

        # 4681 frames in 157 seconds, around 30 fps
        TEST_VIDEO = "../test_data/Ardeer.mp4"
        if not os.path.exists(TEST_VIDEO):
            print("test video not exist")
            print(pathlib.Path(__file__).parent.absolute())
            print(pathlib.Path().absolute())
            return


        cap = cv2.VideoCapture(TEST_VIDEO)  # in all 157 seconds
        if not cap.isOpened():  # check if we succeeded
            print("open video fail...")
            return

        self._cap = cap
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

        self._selection = None
        self._cap = None

    def __del__(self):
        pass
