

def center_crop(cv2_image, width, height):
    h, w = cv2_image.shape[:2]

    x1 = 0 if (w <= width) else (w - width) / 2
    x2 = x1 + width

    y1 = 0 if (h <= height) else (h - height) / 2
    y2 = y1 + height

    result = cv2_image[y1:y2, x1:x2]

    return result


def translate_pt_from_center_crop(pt, center_crop_wh, image_wh):

    assert((center_crop_wh[0] < image_wh[0]) and
           (center_crop_wh[1] < image_wh[1]))

    # Translate <pt> from center cropped ROI frame-of-reference
    # back to source image frame-of-reference
    return (
           ((image_wh[0] / 2) - (center_crop_wh[0] / 2)) + pt[0],
           ((image_wh[1] / 2) - (center_crop_wh[1] / 2)) + pt[1]
    )
