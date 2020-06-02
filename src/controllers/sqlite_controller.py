import sqlite3
import threading
import json
import uuid

import cv2
import time
from .threaded_engine_controller import ThreadedEngineController
import queue
import glob
import sys
import os
import logging
import pathlib


SQLITE3_DB = str(pathlib.Path.cwd()) + "/../mydata.db"

class SqliteController(ThreadedEngineController):
    """
    refactor this part as a controller instead of an engine, because we don't need a real-time database at the moment.
    so, for simplicity move sqlite module from the engine pipeline to a controller
    """

    def __init__(self):

        ThreadedEngineController.__init__(self)

        self._engine_shutdown = False
        self._log = logging.getLogger()
        self._enabled = True

        # sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
        # The object was created in thread id 140557547521856 and this is thread id 140556750186240.
        # self.conn = sqlite3.connect(self.SQLITE3_DB)


    # sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
    # The object was created in thread id 140557547521856 and this is thread id 140556750186240.
    @staticmethod
    def application_engine_insert_sqlite(plate, plate_confidence, processing_time_ms, epoch_time):
        # todo: migrate this later: https://github.com/palantir/sqlite3worker

        # this save should be finished even under the shutdown cmd
        conn = sqlite3.connect(SQLITE3_DB)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO OPENALPR \
                        (UUID, PLATE, CONFIDENCE, PROCESSING_TIME_MS, EPOCH_TIME) \
                          VALUES (?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), plate, plate_confidence, processing_time_ms, epoch_time))
        conn.commit()
        cursor.close()
        conn.close()

    # def application_engine_insert_sqlite(self, plate, plate_confidence, processing_time_ms, epoch_time):
    #
    #     # this save should be finished even under the shutdown cmd
    #
    #     cursor = self.conn.cursor()
    #
    #     cursor.execute("INSERT INTO OPENALPR \
    #                     (UUID, PLATE, CONFIDENCE, PROCESSING_TIME_MS, EPOCH_TIME) \
    #                       VALUES (?, ?, ?, ?, ?)",
    #                    (str(uuid.uuid4()), plate, plate_confidence, processing_time_ms, epoch_time))
    #     self.conn.commit()
    #     cursor.close()

    def disable(self):
        self._enabled = False

    def notify_shutdown(self):
        self._engine_shutdown = True

    def notify_insert_sqlite(self, plate, plate_confidence, processing_time_ms, epoch_time):

        # self.application_engine_insert_sqlite(plate, plate_confidence, processing_time_ms, epoch_time)
        t = threading.Thread(target=SqliteController.application_engine_insert_sqlite,
                             args=(plate, plate_confidence, processing_time_ms, epoch_time))
        t.start()

    def run(self):
        # todo: reserve for multi-threads sqlite management
        # todo: look at this: https://github.com/palantir/sqlite3worker
        while not self._engine_shutdown:
            if not self._enabled:
                time.sleep(0.5)
                continue
