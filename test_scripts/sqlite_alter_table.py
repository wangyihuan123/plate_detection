import sqlite3

# caution: This api would drop the existed table first!
def alter_table_openalpr2():
    conn=sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    drop_table = '''DROP TABLE IF EXISTS OPENALPR;'''
    cursor.execute(drop_table)

    create_table = '''CREATE TABLE IF NOT EXISTS OPENALPR
       (UUID                    TEXT PRIMARY KEY  NOT NULL,
       PLATE                    TEXT  NOT NULL,
       CONFIDENCE               TEXT  NOT NULL,
       PROCESSING_TIME_TOTAL    FLOAT NOT NULL,
       PROCESSING_TIME_PLATES   FLOAT NOT NULL,
       PROCESSING_TIME_VEHICLES FLOAT NOT NULL,
       EPOCH_TIME               INT NOT NULL
       );'''
    cursor.execute(create_table)
    cursor.close()
    conn.close()
    print("altered new table")

def alter_table_openalpr():
    conn=sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    drop_table = '''DROP TABLE IF EXISTS OPENALPR;'''
    cursor.execute(drop_table)

    create_table = '''CREATE TABLE IF NOT EXISTS OPENALPR
       (UUID                    TEXT PRIMARY KEY  NOT NULL,
       PLATE                    TEXT  NOT NULL,
       CONFIDENCE               FLOAT  NOT NULL,
       PROCESSING_TIME_MS       FLOAT NOT NULL,
       EPOCH_TIME               INT NOT NULL
       );'''
    cursor.execute(create_table)
    cursor.close()
    conn.close()
    print("altered new table")

if __name__ == '__main__':
    alter_table_openalpr()