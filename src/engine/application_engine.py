import json
import traceback
import weakref
import threading
import time as t
import logging
import queue
from controllers import EngineController
from .frame_grabber import FrameGrabber
from .jsonresult_testing_engine import JsonresultTestingEngine
from .openalpr_engine import OpenalprEngine
from .preprocessing_engine import PreprocessingEngine

MAX_FRAME_Q_SIZE = 10  # this is a buffer of how many frames to be latent with
MAX_COMMAND_Q_SIZE = 10



class ApplicationEngine(threading.Thread):

    PLATE_CONFIRMED_TIMES = 2  # 2 for testing, 3 or more for release
    PLATE_CONFIDENCE_THRESHOLD = 60  # if the confidence is too low, it's better not to trust the result

    def __init__(self, headless=False):
        threading.Thread.__init__(self)

        self._headless = headless
        self._command_queue = queue.Queue(MAX_COMMAND_Q_SIZE)
        self._shutdown_cmd = None
        self._log = logging.getLogger()
        self._queue_engines = []

        self._application_engine_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)

        self._controllers = []

        self.dirty_exit = False

        self._plate = dict()

    def __del__(self):
        for c in self._controllers:
            try:
                c._set_engine(None)
            except ReferenceError:
                pass

    def register_controller(self, controller):
        p = weakref.proxy(controller)
        if p not in self._controllers:
            self._controllers.append(p)
            controller._set_engine(self)

    def deregister_controller(self, controller):
        p = weakref.proxy(controller)
        if p in self._controllers:
            self._controllers.remove(p)

    def post_command(self, command):
        print("command", command)
        if command == EngineController.CMD_SHUTDOWN:
            # Shutdown commands considered "out-of-band" and processed next rather than being queued
            self._shutdown_cmd = command
        else:
            # If queue full discard oldest command
            if self._command_queue.full():
                self._command_queue.get(block=False)

            self._command_queue.put(command)

    def clean_outdated_plates(self):
        if len(self._plates) > 0:
            # check
            outdated_plates = []
            for plate, data in self._plates.items():
                if t.time() - data["last_epoch_time"] > 3600 * 2:  # set 2 hours now
                    outdated_plates.append(plate)

            # clean
            for plate in outdated_plates:
                del self._plates[plate]

    def run_application(self):

        self._plates = dict()

        for e in self._queue_engines:
            e.start()


        print("start application_engine")
        while True:

            # dequeue finished frames and notify controllers
            if not self._application_engine_frame_queue.empty():
                nextFrame = self._application_engine_frame_queue.get(block=False)
                if nextFrame is not None:

                    # check all
                    json_result = nextFrame.getDetectionResult()

                    if json_result["error"] == "false":
                        print(json_result["error_code"])
                        print(json_result["error"])
                        continue

                    if json_result["results"] is None:
                        print("No result from openalpr")
                        continue

                    print("************************************************")
                    # print(json.dumps(json_result, indent=2))
                    detected_objects = json_result["results"]

                    # Since there may have several cars or plates in one image, or maybe video in the future
                    # epoch time can be used to identify one request/response from alpr cloud api
                    #
                    epoch_time = json_result["epoch_time"]

                    if len(detected_objects) == 0:
                        # can't detect any plate
                        continue

                    print("---------------------------------------")
                    for car in detected_objects:
                        good_detection_flag = True
                        plate = car["plate"]  # todo: do I need to double check the plate?
                        plate_confidence = car["confidence"]
                        if plate_confidence < self.PLATE_CONFIDENCE_THRESHOLD:
                            good_detection_flag = False
                            continue

                        # angle check: skip if  bad angle? 30 degree?
                        orientation = car["vehicle"]["orientation"][0]  # only get the orientation with the highest confidence
                        if orientation["confidence"] > 90:
                            if orientation["name"] > 30:
                                good_detection_flag = False
                                continue

                        processing_time_ms = car["processing_time_ms"]
                        print("[Plate]: {}, [Confidence]: {}, [Processing_time]: {}".format(plate, plate_confidence,
                                                                                            processing_time_ms))

                        # always update, but need to clean outdated records
                        if plate in self._plates:
                            self._plates[plate] = {"detected_times":self._plates[plate]["detected_times"] + 1,
                                                   "last_epoch_time": epoch_time}
                        else:
                            self._plates[plate] = {"detected_times":1, "last_epoch_time": epoch_time}

                        if self._plates[plate]["detected_times"] >= self.PLATE_CONFIRMED_TIMES:

                            print("Double/Triple confirmed", plate)
                            self._notify_controllers_of_insert_sqlite(plate, plate_confidence, processing_time_ms, epoch_time)
                            self._notify_controllers_of_save_files(nextFrame)

                    # other post-processing
                    # self._notify_controllers_of_frame(nextFrame)

            # check and clean all outdated records
            self.clean_outdated_plates()

            if self._shutdown_cmd is not None:
                return None

            # check command queue
            while not self._command_queue.empty():
                cmd = self._command_queue.get(block=False)

                if cmd == EngineController.CMD_COMPLETE_CAPTURE:
                    self._notify_controllers_of_capture_completion()
                    return None


    def _notify_controllers_of_frame(self, frameData):
        for c in self._controllers[:]:
            try:
                c.notify_frame_data(frameData)
            except ReferenceError:
                self._controllers.remove(c)

    def _notify_controllers_of_shutdown(self):
        for c in self._controllers[:]:
            try:
                c.notify_shutdown()
            except ReferenceError:
                self._controllers.remove(c)

    def _notify_controllers_of_start(self):
        for c in self._controllers[:]:
            try:
                c.notify_start()
            except ReferenceError:
                self._controllers.remove(c)

    def _notify_controllers_of_insert_sqlite(self, plate, plate_confidence, processing_time_ms, epoch_time):

        for c in self._controllers[:]:
            try:
                c.notify_insert_sqlite(plate, plate_confidence, processing_time_ms, epoch_time)
            except ReferenceError:
                self._controllers.remove(c)

    def _notify_controllers_of_save_files(self, frames):

        for c in self._controllers[:]:
            try:
                c.notify_save_files(frames)
            except ReferenceError:
                self._controllers.remove(c)

    def config_openalpr_pipeline(self):
        openalpr_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)
        preprocessing_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)

        self._queue_engines.append(OpenalprEngine(openalpr_frame_queue, self._application_engine_frame_queue))
        self._queue_engines.append(PreprocessingEngine(preprocessing_frame_queue, openalpr_frame_queue))
        self._queue_engines.append(FrameGrabber(preprocessing_frame_queue, self._headless))

    def config_jsonresult_testing_pipeline(self):
        jsonresult_testing_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)
        preprocessing_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)

        self._queue_engines.append(JsonresultTestingEngine(jsonresult_testing_frame_queue, self._application_engine_frame_queue))
        self._queue_engines.append(PreprocessingEngine(preprocessing_frame_queue, jsonresult_testing_frame_queue))
        self._queue_engines.append(FrameGrabber(preprocessing_frame_queue, self._headless))



    def run(self):
        try:
            try:
                self._notify_controllers_of_start()

                # Create and Wire together the pipeline of engines

                # jsonresult pipeline for testing
                # self.config_jsonresult_testing_pipeline()

                # openalpr pipeline
                self.config_openalpr_pipeline()
                # todo:

                state_func = self.run_application

                while state_func is not None:
                    state_func = state_func()

            except Exception as e:
                print("ApplicationEngine.run() - unexpected exception \n {} \n {}".format(str(e), traceback.format_exc()))
                self._log.error("ApplicationEngine.run() - unexpected exception \n {} \n {}".format(str(e), traceback.format_exc()))

                self.dirty_exit = True
            except:
                self._log.error("ApplicationEngine.run() - unexpected exception \n %s" % traceback.format_exc())
        finally:

            while self._queue_engines:
                e = self._queue_engines.pop(0)
                try:
                    e.stop()
                except Exception as e:
                    pass

            self._notify_controllers_of_shutdown()
