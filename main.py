import base64
import uuid
import cv2
import sys
import os
import datetime
import time
import argparse
import subprocess
import sqlite3
import requests
import base64
import json


TEST_FRAMES = [300, 1200, 1800, 2200, 2700, 3000, 3600, 4000, 4500]
# TEST_PLATES = ["WAX081", "XFG774", "1HG9TF", "WCW856", "ZPR916", "1FL2KF", "1JQ7RG","unknown", "AXZ074"]  # the last second is unknown


# 4681 frames in 157 seconds, around 30 fps
TEST_VIDEO = "./test_data/Ardeer.mp4"

# OPENALPR_CLOUD_SECRET_KEY = 'sk_013361c164cbbedb0b82f609'  #d
OPENALPR_CLOUD_SECRET_KEY = 'sk_909a58e3f424cf0db07b7583'

def insert_data(uuid, plate, confidence, processing_time_ms, epoch_time):
    conn = sqlite3.connect('./mydata.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO OPENALPR \
                    (UUID, PLATE, CONFIDENCE, PROCESSING_TIME_MS, EPOCH_TIME) \
                      VALUES (?, ?, ?, ?, ?)",
                   (uuid, plate, confidence, processing_time_ms, epoch_time))
    conn.commit()
    cursor.close()
    conn.close()
    print("Inserted data.")



def openalpr_cloud(image):
    success, encoded_image = cv2.imencode('.png', image)
    img_base64 = base64.b64encode(encoded_image.tobytes())

    url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=nz&secret_key=%s' % (
        OPENALPR_CLOUD_SECRET_KEY)
    r = requests.post(url, data=img_base64)
    if r is not None:
        return r.json()

    return None


def denoising(image, debug):
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    # cv.fastNlMeansDenoisingColoredMulti()

    if debug:
        cv2.imwrite("frame_denoise.png", denoised_image)

    return denoised_image


def debug_image(image, image_count):
    cv2.imshow('image', image)

    # key control
    k = cv2.waitKey(1)
    k = k & 0xFF
    if k == ord('q'):
        print("========= Quit by command ==========")
        sys.exit()

    # save the image for easy check
    image_name = "./running_data/frame_" + str(image_count) + ".png"
    if not os.path.exists(image_name):
        cv2.imwrite(image_name, image)

def main(debug):
    cv2.namedWindow('image')
    cap = cv2.VideoCapture(TEST_VIDEO)  # in all 157 seconds
    if not cap.isOpened():  # check if we succeeded
        print("open video fail...")
        sys.exit()

    try:
        image_count = 0  # the number of frame in the video
        while True:
            image_count += 1
            grab_time = datetime.datetime.now()
            ret, image = cap.read()
            if debug:
                print("[grab frame time]: {}".format( datetime.datetime.now() -  grab_time))

            if ret is not True:
                print("Ending")
                print("{} frames in the test video".format(image_count))  # 4681 frames in all
                sys.exit()

            if image is None:
                print("image is None")
                print(image_count)
                break

            # only for testing
            if image_count not in TEST_FRAMES:
                continue

            # for debug
            if debug:
                debug_image(image, image_count)
                print("------------- Frame {} ----------------".format(image_count))

            # check image quality: blur image
            # todo: use multiple images for denoising or super-
            sharpness = cv2.Laplacian(image, cv2.CV_64F).var()
            if sharpness < 80:
                continue

            # for easy testing and debugging:
            # Skip detection from cloud api, if the frame has been already detected before
            jsonresult_name = "./running_data/openalpr_cloud_result_" + str(image_count) + ".json"
            if not os.path.exists(jsonresult_name):
                start_time = time.time()
                json_result = openalpr_cloud(image)
                stop_time = time.time()
                openalpr_time = stop_time - start_time
                print("From cloud api - [Openalpr Time]: {}".format(openalpr_time), flush=True)

                if json_result is None:
                    print("Error Frame {}: json result from openalpr is None. ".format(image_count))
                    continue

                # write the result to a json file to save my cloud account credit
                with open(jsonresult_name, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, ensure_ascii=False, indent=4)

            else:
                with open(jsonresult_name, 'r') as f:
                    json_result = json.load(f)


            if json_result["error"] == "false":
                print(json_result["error_code"])
                print(json_result["error"])
                continue

            if json_result["results"] is None:
                print("No result from openalpr")
                continue

            print("************************************************")
            print(json.dumps(json_result, indent=2))
            detected_objects = json_result["results"]

            # Since there may have several cars or plates in one image, or maybe video in the future
            # epoch time can be used to identify one request/response from alpr cloud api
            #
            epoch_time = json_result["epoch_time"]
            print("epoch_time", epoch_time)

            print("---------------------------------------")
            for car in detected_objects:
                plate = car["plate"]
                plate_confidence = car["confidence"]
                processing_time_ms = car["processing_time_ms"]
                print("[Plate]: {}, [Confidence]: {}, [Processing_time]: {}".format(plate, plate_confidence,
                                                                                    processing_time_ms))

                # angle check: skip if  bad angle? 30 degree?
                # orientation = car["vehicle"]["orientation"][0]  # only get the orientation with the highest confidence
                # if orientation["confidence"] > 90:
                #     if orientation["name"] > 30:
                #         continue

                start_time = time.time()
                id = str(uuid.uuid4())
                insert_data(id, plate, plate_confidence, processing_time_ms, epoch_time)
                stop_time = time.time()
                sqlite_time = stop_time - start_time
                print("[Sqlite Time]: {}".format(sqlite_time))

    except Exception as ex:
        print(ex)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    message = "Rush Digital Plate Recognition"
    parser = argparse.ArgumentParser(description=message)

    parser.add_argument('--debug',
                        action='store_true',
                        help='Print all debug info')

    args = parser.parse_args()
    main(args.debug)
