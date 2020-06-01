import json
import os
import cv2
from .base_engine import BaseQueueEngine


class PreprocessingEngine(BaseQueueEngine):

    """docstring for BoundaryDetector"""
    def __init__(self, input_queue, output_queue):
        super(PreprocessingEngine, self).__init__(input_queue, output_queue)

    def stop(self):
        super(PreprocessingEngine, self).stop()

    def denoising(self, image):
        denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        # cv.fastNlMeansDenoisingColoredMulti()

        return denoised_image

    def process(self, nextFrame):

        # here can be extended to run a super-resolution model, just need to maintain another internal list/dictionary
        frame = nextFrame.getTextureImage()

        # todo: check bad angle or bad condition?

        nextFrame.updateTextureImage(self.denoising(frame))

