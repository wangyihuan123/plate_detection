import json
import uuid
import traceback
import weakref
import threading
import time as t
import collections
import logging
import queue
from controllers import EngineController
from .frame_grabber import FrameGrabber
from .jsonresult_testing_engine import JsonresultTestingEngine
# from .openalpr_engine import OpenalprEngine
from .openalpr_engine import OpenalprEngine
from .preprocessing_engine import PreprocessingEngine

MAX_FRAME_Q_SIZE = 10  # this is a buffer of how many frames to be latent with
MAX_COMMAND_Q_SIZE = 10

MEASUREMENT_CONFIRMED = 2

ScaledLog = collections.namedtuple("ScaledLog", ["uuid",
                                                 "session",
                                                 "ticket",
                                                 "ticketCoordinates",
                                                 "detectedLog",
                                                 "textureImage",
                                                 "depthImage",
                                                 "intrinsics",
                                                 "depthScale",
                                                 "qualityScore",
                                                 "timestamp"])


class ApplicationEngine(threading.Thread):

    CONTROLLER_STATE_INACTIVE = 0
    CONTROLLER_STATE_IDLE = 1
    CONTROLLER_STATE_RUNNING_CAPTURE = 2

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


    def _state_func__run_capture(self):

        self._plates = dict()
        self._trigger_down = False

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
                    print("epoch_time", epoch_time)


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


                        if plate in self._plates:
                            self._plates[plate] += 1
                        else:
                            self._plates[plate] = 1

                        if self._plates[plate] >= self.PLATE_CONFIRMED_TIMES:
                            self._notify_controllers_of_insert_sqlite(plate, plate_confidence, processing_time_ms, epoch_time)
                            self._notify_controllers_of_save_files(nextFrame)

                    # other post-processing
                    # self._notify_controllers_of_frame(nextFrame)



            if self._shutdown_cmd is not None:
                return None

            while not self._command_queue.empty():
                cmd = self._command_queue.get(block=False)

                if cmd == EngineController.CMD_COMPLETE_CAPTURE:
                    self._notify_controllers_of_capture_completion()
                    return self._state_func__idle
                if cmd == EngineController.CMD_ABORT_CAPTURE:
                    self._notify_controllers_of_aborted_capture()
                    return self._state_func__idle

                if cmd == EngineController.CMD_TRIGGER_DOWN:
                    self._current_ticket = None
                    self._trigger_down = True
                    current_trigger_uuid = str(uuid.uuid4())
                    self._notify_controllers_of_trigger_state(True, current_trigger_uuid)
                    self._notify_engines_of_trigger_state(True)
                if cmd == EngineController.CMD_TRIGGER_UP:
                    self._trigger_down = False
                    self._notify_controllers_of_trigger_state(False)
                    self._notify_engines_of_trigger_state(False)
                    if self._current_ticket is not None:
                        self._notify_controllers_of_upload_log(self._scaled_logs[current_trigger_uuid])


    def _state_func__idle(self):


        for e in self._queue_engines:
            e.stop()

        # self._trigger_down = False
        # self._notify_controllers_of_state_update(ApplicationEngine.CONTROLLER_STATE_IDLE, "Idle")

        while True:
            t.sleep(0.05)

            if self._shutdown_cmd is not None:
                return None

            while not self._command_queue.empty():
                cmd = self._command_queue.get(block=False)

                if cmd == EngineController.CMD_START_CAPTURE:
                    return self._state_func__run_capture

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

    def _notify_controllers_of_upload_capture(self):

        for c in self._controllers[:]:
            try:
                c.notify_upload_capture()
            except ReferenceError:
                self._controllers.remove(c)

    def _notify_controllers_of_upload_log(self, log):

        for c in self._controllers[:]:
            try:
                c.notify_upload_log(log)
            except ReferenceError:
                # Shouldn't happen as controllers deregister themselves upon destruction
                self._controllers.remove(c)


    def run(self):
        try:
            try:

                self._notify_controllers_of_start()
                # self._notify_controllers_of_state_update(ApplicationEngine.CONTROLLER_STATE_INACTIVE, "Initialising")

                # todo: move this part to _state_func__run_capture

                # Create and Wire together the pipeline of engines
                # jsonresult_testing_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)
                # preprocessing_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)
                #
                # self._queue_engines.append(JsonresultTestingEngine(jsonresult_testing_frame_queue, self._application_engine_frame_queue))
                # self._queue_engines.append(PreprocessingEngine(preprocessing_frame_queue, jsonresult_testing_frame_queue))
                # self._queue_engines.append(FrameGrabber(preprocessing_frame_queue, self._headless))

                # openalpr pipeline
                openalpr_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)
                preprocessing_frame_queue = queue.Queue(MAX_FRAME_Q_SIZE)

                self._queue_engines.append(OpenalprEngine(openalpr_frame_queue, self._application_engine_frame_queue))
                self._queue_engines.append(PreprocessingEngine(preprocessing_frame_queue, openalpr_frame_queue))
                self._queue_engines.append(FrameGrabber(preprocessing_frame_queue, self._headless))
                # todo:

                # first state - enter IDLE
                # state_func = self._state_func__test
                state_func = self._state_func__run_capture

                while state_func is not None:
                    state_func = state_func()

            except Exception as e:
                print("ApplicationEngine.run() - unexpected exception \n %s \n %s" % (str(e), traceback.format_exc()))
                self._log.error("ImageCaptureEngine.run() - unexpected exception \n %s \n %s" % (str(e), traceback.format_exc()))

                self.dirty_exit = True
            except:
                self._log.error("ImageCaptureEngine.run() - unexpected exception \n %s" % traceback.format_exc())
        finally:

            # todo: move this part to _state_func__run_capture
            while self._queue_engines:
                e = self._queue_engines.pop(0)
                try:
                    e.stop()
                except Exception as e:
                    pass
            # todo:

            self._notify_controllers_of_shutdown()
