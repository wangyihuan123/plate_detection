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
        self._ticketROI = None
        self._tickets = None
        self._detect_box = None
        self._depth_detect_box = None
        self._detect_center_distance = None
        self._detect_area = None
        self._plane_roi = None
        self._plane_centroid = None
        self._plane_direction = None
        self._pitch = None
        self._yaw = None
        self._cameraPoseOkay = False
        self._greyValue = 0
        self._greyDelta = 0
        self._greyDeltaOkay = False
        self._quality_score = None
        self._polygon_points = None
        self._point3d = None
        self._point2d = None
        self._plane_map = None


        self._frame = frame

        if not headless:
            self._display_depth_image = frame

    def dumpFrame(self):

        frame_uuid = str(self._frame_id)

        cv2.imwrite(frame_uuid + '-texture.png', self.getTextureImage())

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


    def getDepthDisplayImage(self):
        return self._display_depth_image

    def getTextureImage(self):
        return self._frame

    def updateTextureImage(self, texture_image):
        self._frame = texture_image

    def setDetectionResult(self, detection_result):
        self._json_result = detection_result

    def getDetectionResult(self):
        return self._json_result
