import numpy as np
import cv2
import sys
import os
import json
import collections
import time
import datetime

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))



groundtruth_plates = ['S7002951', 'S7002952', 'S7002953', 'S7002954', 'S7002955', 'S7002956', 'S7002957', 'S7002958', 'S7002959', 'S7002960', 'S7002961', 'S7002962', 'S7002963', 'S7002964', 'S7002965', 'S7002966', 'S7002967', 'S7002968', 'S7002969', 'S7002970', 'S7002971', 'S7002972', 'S7002973', 'S7002974', 'S7002975', 'S7002976', 'S7002977', 'S7002978', 'S7002979', 'S7002980', 'S7002981', 'S7002982', 'S7002983', 'S7002984', 'S7002985', 'S7002986', 'S7002987', 'S7002988', 'S7002989', 'S7002990', 'S7002991', 'S7002992', 'S7002993', 'S7002994', 'S7002995']

def main():

    cap = cv2.VideoCapture("Ardeer.mp4")
    if not cap.isOpened(): # check if we succeeded
        print("open video fail...")
        sys.exit()

    tickets_sn_lists = []
    unique_list = []
    the_whole_time = datetime.datetime.now()
    first_ticket_time = 0
    # idle_time = 0
    start_first_ticket_timer = 0

    try:

        while True:

            grab_time = datetime.datetime.now()

            ret, image = cap.read()

            print("grab time: {}".format( datetime.datetime.now() -  grab_time))

            if ret is not True:
                print("Ending")
                # time.sleep(2)

            if image is None:
                break

            # image = image_utils.ensure_grayscale(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            barcode_time = datetime.datetime.now()

            # tickets_in_image = barcode.find_dmtx(image,
            #                                      t=1000,
            #                                      min_e=10,
            #                                      max_e=1000,
            #                                      maxcount=max_count)
            # print( "barcode time: {}".format(datetime.datetime.now() -  barcode_time))
            #
            # # print(tickets_in_image)
            # # loop all the tickets found in the image
            # i = len(tickets_in_image)
            #
            # if i == 0:
            #     # print("normal: Exposure time: {} Gain:{}".format(chunk["ChunkExposureTime"], chunk["ChunkGainAll"]))
            #     pass
            # else :
            #     # print("catch: Exposure time: {} Gain:{}".format(chunk["ChunkExposureTime"], chunk["ChunkGainAll"]))
            #
            #     if start_first_ticket_timer == 0:
            #         first_ticket_time = datetime.datetime.now()
            #         start_first_ticket_timer = 1
            #
            #     while  i > 0:
            #         j = i-1
            #         # print(tickets_in_image.items()[j])
            #         dtmx_code_coords = tickets_in_image.items()[j][1]
            #         dtmx_code_coords = np.round(np.array(dtmx_code_coords)).astype(np.int)
            #         #cv2.polylines(image, [dtmx_code_coords], True, (0, 255, 255))
            #         # cv2.polylines(image, [dtmx_code_coords], True, (0, 255, 255), 2)
            #         tickets_sn_lists.append(tickets_in_image.items()[j][0])
            #         i -= 1
            #
            #     unique_list = sorted(set(tickets_sn_lists))
            #     if len(np.intersect1d(unique_list, validation_code_45)) == 45:
            #         # we found all
            #         break
            #
            #     # print("----------------")

            # for debug
            cv2.namedWindow('image')
            cv2.imshow('image', image)

            k = cv2.waitKey(1)
            k = k & 0xFF


            if k == ord('q'):
                print("========= Quit by command ==========")
                break

        # unique_list_counter = len(unique_list)
        # # print("\n\nValidation list count: {}\n".format(unique_list_counter))
        # # print(unique_list)
        #
        #
        # print("========== Result Statistics ==========\n")
        #
        #
        # if np.array_equal(unique_list, validation_code_45):
        #     print("**********************************************************")
        #     print("========== Perfect! You get all exact 45 tickets! ========")
        #     print("**********************************************************\n")
        #
        # print("  -------------- Time -------------:")
        # now = datetime.datetime.now()
        # print("The whole time:                   {}".format(now - the_whole_time))
        # print("Start from the first ticket:      {} \n".format(now - first_ticket_time))
        # # print("Average find_dmtx time")
        # # print("Idle time")
        #
        #
        # missing_tickets = np.setdiff1d(validation_code_45, unique_list )
        # missing_counter = len(missing_tickets)
        # print("  ---- Missing Tickets ---- : ")
        # print(missing_tickets)
        # print("Missing count: {} \n".format(missing_counter))
        # # print("Mising Percentage: {}".format(missing_counter/validation_list_counter))
        #
        # wrong_tickets = np.setdiff1d(unique_list, validation_code_45)
        # wrong_counter = len(wrong_tickets)
        # # another way is to use np.in1d()
        # print("  ---- Wrong Tickets ----:")
        # print(wrong_tickets)
        # print("Wrong count: {} \n".format(wrong_counter))
        # # print("Wrong Percentage:")
        #
        # correct_tickets = np.intersect1d(unique_list, validation_code_45)
        # correct_counter = len(correct_tickets)
        # print("  ---- Correct Tickets ----:")
        # print(correct_tickets)
        # print("Correct count: {} \n".format(correct_counter))
        # print("\n")
        # # print("Correct Percentage:")


    except:
        os.abort


    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()