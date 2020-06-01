import json
import os
from .base_engine import BaseQueueEngine
import pathlib

class JsonresultTestingEngine(BaseQueueEngine):

    """docstring for BoundaryDetector"""
    def __init__(self, input_queue, output_queue):
        super(JsonresultTestingEngine, self).__init__(input_queue, output_queue)
        self.jsonresult_dir = str(pathlib.Path.cwd()) + "../../running_data/"

    def stop(self):
        super(JsonresultTestingEngine, self).stop()

    def process(self, nextFrame):
        # image_count = 1200
        image_count = nextFrame.getFrameId()
        jsonresult_name = pathlib.Path.joinpath(self.jsonresult_dir, "openalpr_cloud_result_" + str(image_count) + ".json")
        if not os.path.exists(jsonresult_name):
            print("????? {} not exist????".format(jsonresult_name))
            return False


        with open(jsonresult_name, 'r') as f:
            json_result = json.load(f)

        nextFrame.setDetectionResult(json_result)

        return True

