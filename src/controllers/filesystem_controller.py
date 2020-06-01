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
FILE_EXTENSIONS = ['*.jpg', '*.json', '*.npz']  # these type file will be uploaded to aws

DEFAULT_REGION_NAME = 'ap-southeast-2'
DEFAULT_AWS_ACCESS_KEY = 'AKIAJQBUX2SIGV2Z377Q'
DEFAULT_AWS_SECRET_ACCESS_KEY = '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'
DEFAULT_AWS_BUCKET_NAME = 'c3.scaling.images'

date_format = '%Y-%m-%dT%H:%M:%S%z'


image_extn = '.png'
json_extn = '.json'
depth_extn = '.npz'


class FilesystemController(ThreadedEngineController):
    """
    1. All the texture images, depth images, detectionresult json saved in the output_dir before upload
    2. saved_summary.log and uploaded_summary.log record all the saved and uploaded files
    3. heartbeat_run() only check whether or not we can contact aws S3 bucket
    4. After being uploaded, the local files in output dir would be deleted

    """
    def __init__(self):

        ThreadedEngineController.__init__(self)

        self._engine_shutdown = False
        self._log = logging.getLogger()
        self._enabled = True

        output_dir = Path().resolve().parent
        output_dir = os.path.join(output_dir, DATA_DIR)
        print(output_dir)

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

        print(os.path.exists(detectionresult_filename))

    def disable(self):
        self._enabled = False

    # def _spool_existing_jobs(self):
    #
    #     files = []
    #     for extn in FILE_EXTENSIONS:
    #         files.extend(glob.glob(self.output_dir + os.sep + extn))
    #
    #     for file in files:
    #         self._work_q.put(file)
    #
    # def notify_start(self):
    #     self._work_q = queue.Queue()
    #
    #     if self._enabled:
    #         self._spool_existing_jobs()
    #     ThreadedEngineController.notify_start(self)


    def notify_start_capture(self, session_uuid):
        self._sent_tickets = []
        self._session_uuid = session_uuid

    def notify_completed_capture(self):
        self._sent_tickets = []
        self._session_uuid = None

    def notify_aborted_capture(self):
        self._sent_tickets = []
        self._session_uuid = None

    def notify_shutdown(self):
        self._engine_shutdown = True


    def notify_save_files(self, frame):
        image = frame.getTextureImage()
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


