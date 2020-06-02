import threading
import json
import uuid
from pathlib import Path
import cv2
import time
from .threaded_engine_controller import ThreadedEngineController
import queue
import glob
import sys
import os
import logging

DATA_DIR = 'running_data'
image_extn = '.png'
json_extn = '.json'


class FilesystemController(ThreadedEngineController):
    """
    All the detectionresult json and image files saved in the output_dir for further review or test
    """
    def __init__(self):

        ThreadedEngineController.__init__(self)

        self._engine_shutdown = False
        self._log = logging.getLogger()
        self._enabled = True

        output_dir = Path().resolve().parent
        output_dir = os.path.join(output_dir, DATA_DIR)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        self.output_dir = output_dir

    # update summery txt log
    def update_summary_file(self, file_job, summary_file):
        file_job = os.path.basename(file_job)

        with open(summary_file, "a") as f:
            f.write(time.ctime() + "\t" + file_job + "\n")


    @staticmethod
    def application_engine_file_writer(output_dir, image2, frame_id,  json_result2):

        image_file_basename = 'frame'
        detectionresult_file_basename = 'openalpr_cloud_result'
        suffix = str(frame_id)
        # ==============================================================================================

        # save the image
        image_filename = output_dir + os.sep + image_file_basename + "_" + suffix + image_extn
        if not os.path.exists(image_filename):
            cv2.imwrite(image_filename, image2)

        # save the detection result json file
        detectionresult_filename = output_dir + os.sep + detectionresult_file_basename + "_" + suffix + json_extn
        if not os.path.exists(detectionresult_filename):
            detectionresult_json_data = json_result2
            with open(detectionresult_filename, 'w') as f:
                json.dump(detectionresult_json_data, f, ensure_ascii=False, indent=4)


    def disable(self):
        self._enabled = False


    def notify_shutdown(self):
        self._engine_shutdown = True


    def notify_frame_data(self, frame):
        image = frame.getImage()
        frame_id = frame.getFrameId()
        json_result3 = frame.getDetectionResult()
        t = threading.Thread(target=FilesystemController.application_engine_file_writer,
                             args=(self.output_dir, image, frame_id,  json_result3))
        t.start()

    def run(self):

        while not self._engine_shutdown:
            if not self._enabled:
                time.sleep(0.5)
                continue

            # reserve for the furture
            time.sleep(0.5)


