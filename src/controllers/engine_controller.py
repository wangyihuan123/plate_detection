import weakref


import engine


class EngineController(object):

    CMD_SHUTDOWN = 0
    CMD_START_CAPTURE = 1
    CMD_COMPLETE_CAPTURE = 2
    CMD_ABORT_CAPTURE = 3
    CMD_SHUTDOWN = 5
    CMD_TRIGGER_DOWN = 6
    CMD_TRIGGER_UP = 7
    CMD_UPLOAD = 8

    def __init__(self):
        super(EngineController, self).__init__()

        self._engine = None
        self._engine_shutdown = False
        self._session_uuid = None

    def notify_start(self):
        pass

    def notify_shutdown(self):
        self._engine_shutdown = True

    def notify_state_update(self, state, status_txt=""):
        self._controller_state = state
        self._status_txt = status_txt

    def notify_frame_data(self, frameData):
        pass

    def notify_start_capture(self, session_uuid=None):
        self._logs = dict()
        self._session_uuid = session_uuid

    def notify_completed_capture(self):
        self._logs = dict()
        self._session_uuid = None

    def notify_aborted_capture(self):
        self._logs = dict()
        self._session_uuid = None

    # for sqlite controller
    def notify_insert_sqlite(self, plate, plate_confidence, processing_time_ms, epoch_time):
        pass

    # for filesystem_controller
    def notify_save_files(self, frame):
        pass

    def signal_shutdown(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_SHUTDOWN)
            except ReferenceError:
                self._engine = None

    def signal_start_capture(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_START_CAPTURE)
            except ReferenceError:
                self._engine = None

    def signal_complete_capture(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_COMPLETE_CAPTURE)
            except ReferenceError:
                self._engine = None

    def signal_abort_capture(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_ABORT_CAPTURE)
            except ReferenceError:
                self._engine = None

    def signal_trigger_down(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_TRIGGER_DOWN)
            except ReferenceError:
                self._engine = None

    def signal_trigger_up(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_TRIGGER_UP)
            except ReferenceError:
                self._engine = None

    def _set_engine(self, e):
        if e is not None:
            self._engine = weakref.proxy(e)
        else:
            self._engine = None

    def signal_upload(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_UPLOAD)
            except ReferenceError:
                self._engine = None

    def notify_upload_log(self, log):
        pass

    def __del__(self):
        pass
