import cv2
import sys
import os
import datetime

def main():

    cap = cv2.VideoCapture("Ardeer.mp4")
    if not cap.isOpened(): # check if we succeeded
        print("open video fail...")
        sys.exit()

    try:

        while True:

            grab_time = datetime.datetime.now()

            ret, image = cap.read()

            print("grab time: {}".format( datetime.datetime.now() -  grab_time))

            if ret is not True:
                print("Ending")
                # sys.exit()

            if image is None:
                break

            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # for debug
            cv2.namedWindow('image')
            cv2.imshow('image', image)

            k = cv2.waitKey(1)
            k = k & 0xFF


            if k == ord('q'):
                print("========= Quit by command ==========")
                break

    except:
        os.abort


    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()