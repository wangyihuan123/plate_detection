import json
import os
import cv2
from .base_engine import BaseQueueEngine


class PreprocessingEngine(BaseQueueEngine):

    GREYVALUE_THRESHOLD = 10
    SHARPNESS_THRESHOLD = 80
    DENOISING_CLUSTER = 5

    def __init__(self, input_queue, output_queue):
        super(PreprocessingEngine, self).__init__(input_queue, output_queue)
        self._images = []

    def stop(self):
        super(PreprocessingEngine, self).stop()

    def denoising(self, images):
        # todo: need to be optimized later
        # todo: can be extended to multiple images, like cv.fastNlMeansDenoisingColoredMulti
        # todo: Or to run a super-resolution model,
        # need to maintain another internal list/dictionary
        # denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        denoised_image = cv2.fastNlMeansDenoisingMulti(images, 2, 5, None, 4, 7, 35)

        return denoised_image

    def plate_roi_crop(self, cv2_image):
        h, w = cv2_image.shape[:2]  # 1080, 1920

        # we can only focus the low part of the image for this Ardeer.mp4 test video
        # so, set the magic roi for now
        x1 = 100
        y1 = 200
        x2 = 1820
        y2 = 1080
        result = cv2_image[y1:y2, x1:x2]

        return result

    def process(self, nextFrame):

        frame = nextFrame.getImage()

        # solution 1: for a simple case, just use opencv to denoise the image
        # image = self.denoising(frame)

        # solution 2: for a multiple-images case,
        self._images.append(frame)
        if len(self._images) >= self.DENOISING_CLUSTER:
            image = self.denoising(self._images)
            self._images = []
        else:
            return False

        # use greyvalue and sharpness to simply check the bad condition

        # to avoid the images which are too dark:
        # sometimes the camere may be blocked, sometimes lights may be broken, sometimes the whether is terrible
        image_grey_value = image.mean()
        if image_grey_value < self.GREYVALUE_THRESHOLD:
            return False

        # check image quality: skip the blur image
        sharpness = cv2.Laplacian(image, cv2.CV_64F).var()
        if sharpness < self.SHARPNESS_THRESHOLD:
            return False

        # bad angle can be checked based on the result of openalpr response["vehicle"]["orientation"]

        # todo: for motion blur, try DeblurGAN: https://github.com/KupynOrest/DeblurGAN, my  GPU is not good enough to try this

        # todo: It is also a good idea to add another engine to run a real-time object detection model after this preprocessing


        # Limit plate search to central ROI to
        # a) speed up processing, and
        # b) skip, if the detected plate is out of our ROI
        image_roi = self.plate_roi_crop(image)
        # image_roi = image

        nextFrame.updateImage(image_roi)

        return True

