import weakref


import engine


class EngineController(object):

    CMD_SHUTDOWN = 0
    CMD_DEBUG = 1

    def __init__(self):
        super(EngineController, self).__init__()

        self._engine = None
        self._engine_shutdown = False

    def notify_start(self):
        pass

    def notify_shutdown(self):
        self._engine_shutdown = True

    def notify_frame_data(self, frameData):
        pass

    # for sqlite controller
    def notify_insert_sqlite(self, plate, plate_confidence, processing_time_ms, epoch_time):
        pass

    def notify_debug(self, debug):
        pass

    def signal_shutdown(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_SHUTDOWN)
            except ReferenceError:
                self._engine = None

    def signal_debug(self):
        if self._engine is not None:
            try:
                self._engine.post_command(EngineController.CMD_DEBUG)
            except ReferenceError:
                self._engine = None

    def _set_engine(self, e):
        if e is not None:
            self._engine = weakref.proxy(e)
        else:
            self._engine = None

    def __del__(self):
        pass
