import sys, traceback
import threading
import queue
import logging


class BaseQueueEngine(object):
    """docstring for BaseEngine"""
    def __init__(self, input_queue, output_queue):
        super(BaseQueueEngine, self).__init__()
        assert input_queue is not None
        assert output_queue is not None
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._worker_thread = None
        self._running = False
        self._log = logging.getLogger()

    def start(self):
        if not self._running:
            self._running = True
            self._worker_thread = threading.Thread(target=self.run)
            self._worker_thread.start()

    def stop(self):
        if self._running:
            self._running = False
            self._worker_thread.join()
            self._worker_thread = None
            with self._output_queue.mutex:
                self._output_queue.queue.clear()

    def run(self):
        while self._running:
            if not self._input_queue.empty():
                try:
                    nextFrame = self._input_queue.get(block=False)

                    if not self.process(nextFrame):  # interrupt the pipeline if process return false
                        continue

                    if self._output_queue.full():
                        self._output_queue.get(block=False)
                    self._output_queue.put(nextFrame)
                except queue.Empty:
                    pass
                except Exception:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=8, file=sys.stdout)

    # To be implemented by the queue engine component
    def process(self, nextFrame):
        pass

    def __del__(self):
        self._running = False
        if self._worker_thread is not None:
            self._worker_thread.join()
            self._worker_thread = None
