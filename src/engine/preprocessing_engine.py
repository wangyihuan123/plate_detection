import json
import os
import cv2
from .base_engine import BaseQueueEngine


class PreprocessingEngine(BaseQueueEngine):

    GREYVALUE_THRESHOLD = 10
    SHARPNESS_THRESHOLD = 80
    def __init__(self, input_queue, output_queue):
        super(PreprocessingEngine, self).__init__(input_queue, output_queue)

    def stop(self):
        super(PreprocessingEngine, self).stop()

    def denoising(self, image):
        # todo: need to be optimized later
        # todo: can be extended to multiple images, like cv.fastNlMeansDenoisingColoredMulti
        # todo: Or to run a super-resolution model, just need to maintain another internal list/dictionary
        denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

        return denoised_image

    def process(self, nextFrame):

        frame = nextFrame.getTextureImage()

        # currently, for a simple case, just use opencv to denoise the image
        image = self.denoising(frame)

        # use greyvalue and sharpness to simply check the bad condition

        # to avoid the images which are too dark:
        # sometimes the camere may be blocked,
        # sometimes lights may be broken,
        # sometimes the whether is terrible
        image_grey_value = image.mean()
        if image_grey_value < self.GREYVALUE_THRESHOLD:
            return False

        # check image quality: skip the blur image
        sharpness = cv2.Laplacian(image, cv2.CV_64F).var()
        if sharpness < self.SHARPNESS_THRESHOLD:
            return False

        # bad angle can be checked based on the result of openalpr response["vehicle"]["orientation"]

        # todo: if necessary, can run a small object detection model here as well

        nextFrame.updateTextureImage(image)

        return True

