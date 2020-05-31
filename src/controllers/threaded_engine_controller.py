import threading

from .engine_controller import EngineController


class ThreadedEngineController(EngineController):

    def __init__(self):
        super(ThreadedEngineController, self).__init__()

        self._run_thread = False
        self._worker_thread = threading.Thread(target=self.run)
        self._worker_thread.daemon = True

    def notify_start(self):
        if not self._run_thread:
            self._run_thread = True
            self._worker_thread.start()

    def run(self):
        raise Exception("Child controller needs to implement this")
