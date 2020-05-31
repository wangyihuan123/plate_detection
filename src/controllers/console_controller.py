from .engine_controller import EngineController

import engine

import termios
import sys
import os
import signal

from functools import partial
import logging

class ConsoleController(EngineController):
    """A Controller that we can use when we dont want to connect to STDIN - for when we want to run as a service in the background"""

    def __init__(self):
        super(ConsoleController, self).__init__()
        self._log = logging.getLogger()

    def run_main_loop(self):


        try:
            orig_settings = termios.tcgetattr(sys.stdin)
            new_settings = list(orig_settings)
            new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        except termios.error:
            # Modification not available in particular terminal/terminal emulator we're currently running in.
            orig_settings = None


        def handler(self, a, b):
            self._running = False
            self.signal_shutdown()

        bound_term_handler = partial(handler, self)

        signal.signal(signal.SIGTERM, bound_term_handler)

        self._running = True
        try:
            try:
                while self._running:
                    # nothing to do here but spin
                    k = sys.stdin.read(1)[0]  # Blocking call

                    # Mask out all but the equivalent ASCII key code in the low byte
                    k = ord(k) & 0xFF
                    print(k)
                    if k == 32:  # SPACE

                        if self._controller_state == engine.ApplicationEngine.CONTROLLER_STATE_IDLE:
                            self.signal_start_capture()
                        elif self._controller_state == engine.ApplicationEngine.CONTROLLER_STATE_RUNNING_CAPTURE:
                            self.signal_complete_capture()

                    elif k == ord('t'):
                        self.signal_trigger_down()

                    elif k == ord('y'):
                        self.signal_trigger_up()

                    elif k == 27:  # ESC
                        if self._controller_state == engine.ApplicationEngine.CONTROLLER_STATE_RUNNING_CAPTURE:
                            self.signal_abort_capture()
                    elif k == ord('q'):
                        self.signal_shutdown()
                    elif k == ord('u'):
                        self.signal_upload()

            except KeyboardInterrupt:
                    self.signal_shutdown()
        finally:
            if orig_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

    def notify_state_update(self, state, status_txt=""):

        self._controller_state = state

        if state == engine.ApplicationEngine.CONTROLLER_STATE_IDLE:
            print("Capture engine entering IDLE state")
            self._log.info("Capture engine entering IDLE state")
        elif state == engine.ApplicationEngine.CONTROLLER_STATE_RUNNING_CAPTURE:
            print("Capture engine started CAPTURING")
            self._log.info("Capture engine started CAPTURING")

    def notify_shutdown(self):
        super(ConsoleController, self).notify_shutdown()
        print("Capture engine shutting down")
        self._log.info("Capture engine shutting down")
        # Interrupt stdin key reading loop in run().  thread.interrupt_main() doesn't work, but the following does.
        self._running = False
        os.kill(os.getpid(), signal.SIGINT)
