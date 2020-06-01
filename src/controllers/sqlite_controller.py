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
import numpy as np
import logging

"""
design this as a controller instead of an engine, because we don't need a real-time database at the moment. so, for simplicity move this from the engine pipeline to controller
0. the goal is to build a small sqlite database manager
1. create a thread to put the insert execution to support multi-threads condition, because we may do other query before the insertion
2. the run check and loop each execution in the queue, there may have query, insert, update, or delete operations.
 
using queue for each tsqlite insert
"""

SQLITE3_DB = '/home/eva/code/rushdigital/mydata.db'

class SqliteController(ThreadedEngineController):
    """
    1.
    2. The library creates a queue to manage multiple queries sent to the database.
Instead of directly calling the sqlite3 interface, you will call the
Sqlite3Worker which inserts your query into a Queue.Queue() object.  The queries
are processed in the order that they are inserted into the queue (first in,
first out).  In order to ensure that the multiple threads are managed in the
same queue, you will need to pass the same Sqlite3Worker object to each thread.

    """

    def __init__(self):

        ThreadedEngineController.__init__(self)

        self._engine_shutdown = False
        self._log = logging.getLogger()
        self._work_q = None
        self._enabled = True
        self._session_uuid = None

        # sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
        # The object was created in thread id 140557547521856 and this is thread id 140556750186240.
        # self.conn = sqlite3.connect(self.SQLITE3_DB)

    # update summery txt log
    def update_summary_file(self, file_job, summary_file):
        file_job = os.path.basename(file_job)

        with open(summary_file, "a") as f:
            f.write(time.ctime() + "\t" + file_job + "\n")

    # sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
    # The object was created in thread id 140557547521856 and this is thread id 140556750186240.
    @staticmethod
    def application_engine_insert_sqlite(plate, plate_confidence, processing_time_ms, epoch_time):

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
        # reserve for multi-threads sqlite management
        while not self._engine_shutdown:
            if not self._enabled:
                time.sleep(0.5)
                continue
