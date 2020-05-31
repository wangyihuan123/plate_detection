from base_engine import BaseQueueEngine
import sqlite3
import uuid

class SqliteEngine(BaseQueueEngine):
    SQLITE3_DB = 'mydata.db'
    def __init__(self, input_queue, output_queue):
        super(SqliteEngine, self).__init__(input_queue, output_queue)

        self.conn = sqlite3.connect(self.SQLITE3_DB)


    @staticmethod
    def insert_data(conn, plate, plate_confidence, processing_time_ms, epoch_time):
        cursor = conn.cursor()

        cursor.execute("INSERT INTO OPENALPR \
                        (UUID, PLATE, CONFIDENCE, PROCESSING_TIME_MS, EPOCH_TIME) \
                          VALUES (?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), plate, plate_confidence, processing_time_ms, epoch_time))
        conn.commit()
        cursor.close()


    def process(self, nextFrame):

        if not nextFrame.isCameraPoseOkay():
            return

        plate, plate_confidence, processing_time_ms, epoch_time =  nextFrame.getJsonresult()

        # todo: how to deal with the sql ???

    def __del__(self):
        super(SqliteEngine, self).__del__()
        self.conn.close()

