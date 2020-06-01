import uuid
import numpy as np
import cv2
import json
import time


class FrameData():

    def __init__(self, frame, image_id,  headless=False):
        assert frame is not None
        assert image_id is not None

        self._frame_id = image_id  # uuid.uuid4()
        self._timestamp = time.time()
        self._frame = frame

        if not headless:
            self._display_image = frame

    def dumpFrame(self):

        frame_uuid = str(self._frame_id)

        cv2.imwrite(frame_uuid + '.png', self.getImage())

        metadata = {
            "id": frame_uuid,
            "time": self._timestamp
        }

        with open(frame_uuid + '.json', 'w+') as metadata_file:
            json.dump(metadata, metadata_file)

    def getFrameId(self):
        return self._frame_id

    def getTimestamp(self):
        return self._timestamp

    def getDisplayImage(self):
        return self._display_image

    def setDisplayImage(self, image):
        self._display_image = image

    def getImage(self):
        return self._frame

    def updateImage(self, image):
        self._frame = image

    def setDetectionResult(self, detection_result):
        self._json_result = detection_result

    def getDetectionResult(self):
        return self._json_result
