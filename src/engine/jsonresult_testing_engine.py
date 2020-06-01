import json
import os
from .base_engine import BaseQueueEngine


class JsonresultTestingEngine(BaseQueueEngine):

    """docstring for BoundaryDetector"""
    def __init__(self, input_queue, output_queue):
        super(JsonresultTestingEngine, self).__init__(input_queue, output_queue)

    def stop(self):
        super(JsonresultTestingEngine, self).stop()

    def process(self, nextFrame):
        # image_count = 1200
        image_count = nextFrame.getFrameId()
        jsonresult_name = "/home/eva/code/rushdigital/running_data/openalpr_cloud_result_" + str(image_count) + ".json"
        if not os.path.exists(jsonresult_name):
            print("????? {} not exist????".format(jsonresult_name))
            return


        with open(jsonresult_name, 'r') as f:
            json_result = json.load(f)

        nextFrame.setDetectionResult(json_result)

