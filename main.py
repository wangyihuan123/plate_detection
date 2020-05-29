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


def test_openalpr():
    # txt = os.system("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu MY02ZR0.jpg | sed -n '2p'"))
    res = subprocess.getstatusoutput("docker run -it --rm -v $(pwd):/data:ro openalpr -c us frame.png | sed -n '2p'")
    print(res)
    if res[1] is '':
        return None, None

    record = res[1].split("    - ")[1].split("\t confidence: ")
    print(record)
    # return plate_str, confidence
    return record[0], record[1]


def insert_data(uuid, plate, confidence, processing_time_ms, epoch_time):
    conn = sqlite3.connect('./mydata.db')
    cursor = conn.cursor()

    # if not os.path.exists("frame.jpg"):
    #     print("frame.jpg not exist")
    #     return

    cursor.execute("INSERT INTO OPENALPR \
                    (UUID, PLATE, CONFIDENCE, PROCESSING_TIME_MS, EPOCH_TIME) \
                      VALUES (?, ?, ?, ?, ?)",
                   (uuid, plate, confidence, processing_time_ms, epoch_time))
    conn.commit()
    cursor.close()
    conn.close()
    print("Inserted data.")


# OPENALPR_CLOUD_SECRET_KEY = 'sk_013361c164cbbedb0b82f609'  #d
OPENALPR_CLOUD_SECRET_KEY = 'sk_909a58e3f424cf0db07b7583'


def openalpr_cloud(image):
    cv2.imshow('image', image)
    cv2.waitKey()
    print("xxxxxxxxxxxxxxxxxxxxxxxxxx")
    img_base64 = base64.b64encode(image)

    url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=nz&secret_key=%s' % (
        OPENALPR_CLOUD_SECRET_KEY)
    r = requests.post(url, data=img_base64)
    if r is not None:
        return r.json()

    return None


def denoising(img):
    # img = cv2.imread('frame.png')
    dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    # cv.fastNlMeansDenoisingColoredMulti()
    cv2.imwrite("frame_denoise.png", dst)


# TEST_FRAMES = [300, 1200, 1800, 2200, 2700, 3000, 3600, 4000, 4500]
# TEST_PLATES = ["WAX081", "XFG774", "1HG9TF", "WCW856", "ZPR916", "1FL2KF", "1JQ7RG","unknown", "AXZ074"]  # the last second
TEST_FRAMES = [1200, 4000]
TEST_PLATES = ["XFG774", "unknown"]
TEST_VIDEO = "./test_data/Ardeer.mp4"


# 4681 frames in 157 seconds, around 30 fps

def main(debug):
    cv2.namedWindow('image')
    cap = cv2.VideoCapture(TEST_VIDEO)  # in all 157 seconds
    if not cap.isOpened():  # check if we succeeded
        print("open video fail...")
        sys.exit()

    try:
        image_count = 0
        while True:
            image_count += 1
            grab_time = datetime.datetime.now()
            ret, image = cap.read()
            # print("[grab frame time]: {}".format( datetime.datetime.now() -  grab_time))

            if ret is not True:
                print("Ending")
                print("{} frames in the test video".format(image_count))  # 4681 frames in all
                sys.exit()

            if image is None:
                print("image is None")
                print(image_count)
                break

            if image_count not in TEST_FRAMES:
                continue

            # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            imagename = "./running_data/frame_" + str(image_count) + ".png"
            if not os.path.exists(imagename):
                # save_time = time.time()
                cv2.imwrite(imagename, image)
                # print("[save image time]: {}".format( time.time() -  save_time))

            # for debug
            if debug:
                cv2.imshow('image', image)

            # key control
            k = cv2.waitKey(1)
            k = k & 0xFF
            if k == ord('q'):
                print("========= Quit by command ==========")
                break

            print(".....", image_count)

            #
            start_time = time.time()
            json_result = openalpr_cloud(image)
            stop_time = time.time()
            openalpr_time = stop_time - start_time
            print("[Openalpr Time]: {}".format(openalpr_time), flush=True)

            # sys.exit()
            if json_result is None:
                print("No result from openalpr")
                continue
            if json_result["error"] == "false":
                print(json_result["error_code"])
                print(json_result["error"])

            print(json.dumps(json_result, indent=2))

            if json_result["results"] is None:
                print("No result from openalpr")
                continue

            print("************************************************")
            detected_objects = json_result["results"]
            epoch_time = json_result["epoch_time"]
            print("epoch_time", epoch_time)
            # processing_time_total = json_result["processing_time"]["total"]
            # processing_time_plates = json_result["processing_time"]["plates"]
            # processing_time_vehicles = json_result["processing_time"]["vehicles"]

            print(json.dumps(json_result, indent=2))
            print("---------------------------------------")
            for car in detected_objects:
                plate = car["plate"]
                plate_confidence = car["confidence"]
                processing_time_ms = car["processing_time_ms"]
                print("[Plate]: {}, [Confidence]: {}, [Processing_time]: {}".format(plate, plate_confidence,
                                                                                    processing_time_ms))

                # angle check: skip bad angle?30 degree?
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

    #
    parser.add_argument('--verbose', help='Enable debug logging', action="store_true")

    args = parser.parse_args()
    main(args.debug)
