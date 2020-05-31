import base64
import json
import os
import time

import cv2
import requests
from base_engine import BaseQueueEngine
import sqlite3
import uuid

class OpenalprEngine(BaseQueueEngine):
    # OPENALPR_CLOUD_SECRET_KEY = 'sk_013361c164cbbedb0b82f609'  #d
    OPENALPR_CLOUD_SECRET_KEY = 'sk_909a58e3f424cf0db07b7583'

    def __init__(self, input_queue, output_queue):
        super(OpenalprEngine, self).__init__(input_queue, output_queue)

        self.conn = sqlite3.connect(self.SQLITE3_DB)


    @staticmethod
    def openalpr_cloud(image, secret_key):
        success, encoded_image = cv2.imencode('.png', image)
        img_base64 = base64.b64encode(encoded_image.tobytes())

        url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=nz&secret_key=%s' % (secret_key)
        r = requests.post(url, data=img_base64)
        if r is not None:
            return r.json()

        return None

    def process(self, nextFrame):

        if not nextFrame.isCameraPoseOkay():
            return

        frame = nextFrame.getTextureImage()
        image_id = nextFrame.getFrameId()

        start_time = time.time()
        json_result = self.openalpr_cloud(frame, self.OPENALPR_CLOUD_SECRET_KEY)
        stop_time = time.time()
        openalpr_time = stop_time - start_time
        print("From cloud api - [Openalpr Time]: {}".format(openalpr_time), flush=True)

        if json_result is None:
            print("Error Frame {}: json result from openalpr is None. ".format(image_id))
            return

        nextFrame.setDetectionResult(json_result)

        # backup the jsonresult as a file for debugging and testing
        jsonresult_name = "./running_data/openalpr_cloud_result_" + str(image_id) + ".json"
        if os.path.exists(jsonresult_name):
            return

        # write the result to a json file to save my cloud account credit
        with open(jsonresult_name, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=4)



