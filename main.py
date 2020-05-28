import uuid
import cv2
import sys
import os
import datetime
import time
import argparse
import subprocess
import sqlite3

def test_openalpr():
    # txt = os.system("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu MY02ZR0.jpg | sed -n '2p'"))
    res = subprocess.getstatusoutput("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu frame.png | sed -n '2p'")
    print(res)
    if res[1] is '':
        return None, None

    record = res[1].split("    - ")[1].split("\t confidence: ")
    print(record)
    # return plate_str, confidence
    return record[0], record[1]

def insert_data(id, plate, score, time):
    conn = sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    print(id, plate, score, time)
    if not os.path.exists("frame.jpg"):
        print("frame.jpg not exist")
        return

    cursor.execute("INSERT INTO OPENALPR (ID, PLATE,SCORE,SPENT_TIME) \
      VALUES (?, ?, ?, ? )", (id, plate, score, time))
    conn.commit()
    cursor.close
    conn.close()
    print("Inserted data.")




def main(debug):

    cap = cv2.VideoCapture("Ardeer.mp4")
    if not cap.isOpened(): # check if we succeeded
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
                print("{} frames in the test video".format(image_count))  # 4681 frames inall
                sys.exit()

            if image is None:
                print("image is None")
                print(image_count)
                break

            if image_count % 100 != 0:
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            save_time = time.time()
            cv2.imwrite("frame.png", image)
            # print("[save image time]: {}".format( time.time() -  save_time))

            # for debug
            if debug:
                cv2.namedWindow('image')
                cv2.imshow('image', image)

            # key control
            k = cv2.waitKey(1)
            k = k & 0xFF
            if k == ord('q'):
                print("========= Quit by command ==========")
                break

            #
            start_time = time.time()
            plate, score = test_openalpr()
            stop_time = time.time()
            openalpr_time = stop_time - start_time
            print("[Openalpr Time]: {}".format(openalpr_time))

            if plate is None or score is None:
                print("No result from openalpr")
                continue
            print("************************************************")
            print("[Plate]: {}, [Confidence]: {}".format(plate, score))

            #
            start_time = time.time()
            id = str(uuid.uuid4())
            insert_data(id, plate, score, str(openalpr_time))
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