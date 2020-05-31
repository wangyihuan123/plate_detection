from .engine_controller import EngineController

import engine

import os
import signal
import time

from functools import partial
import logging

class HeadlessController(EngineController):
    """A Controller that we can use when we dont want to connect to STDIN - for
    when we want to run as a service in the background"""

    def __init__(self):
        super(HeadlessController, self).__init__()
        self._running = False
        self._log = logging.getLogger()

    def run_main_loop(self):

        def handler(self, a, b):
            self.signal_shutdown()

        bound_term_handler = partial(handler, self)

        signal.signal(signal.SIGTERM, bound_term_handler)
        signal.signal(signal.SIGINT, bound_term_handler)

        self._running = True
        try:
            while self._running:
                # nothing to do here but spin
                time.sleep(0.05)
                continue
        except KeyboardInterrupt:
            pass

    def notify_state_update(self, state, status_txt=""):

        self._controller_state = state

        if state == engine.ApplicationEngine.CONTROLLER_STATE_IDLE:
            print("Capture engine entering IDLE state")
            self._log.info("Capture engine entering IDLE state")
        elif state == engine.ApplicationEngine.CONTROLLER_STATE_RUNNING_CAPTURE:
            print("Capture engine started CAPTURING")
            self._log.info("Capture engine started CAPTURING")

    def notify_shutdown(self):
        self._running = False

        # Interrupt stdin key reading loop in run().
        # thread.interrupt_main() doesn't work, but the following does.
        os.kill(os.getpid(), signal.SIGINT)
