import sqlite3

def creat_table():
    conn=sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    sql = '''CREATE TABLE OPENALPR
       (ID INT PRIMARY KEY     NOT NULL,
       PLATE           TEXT    NOT NULL,
       SCORE            TEXT     NOT NULL,
       TIME         TEXT);'''
    cursor.execute(sql)
    cursor.close()
    conn.close()
    print("created new table")

# caution: This api would drop the existed table first!
def alter_table_openalpr():
    conn=sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    drop_table = '''DROP TABLE IF EXISTS OPENALPR;'''
    cursor.execute(drop_table)

    create_table = '''CREATE TABLE IF NOT EXISTS OPENALPR
       (ID TEXT PRIMARY KEY     NOT NULL,
       PLATE           TEXT    NOT NULL,
       SCORE            TEXT     NOT NULL,
       SPENT_TIME         TEXT);'''
    cursor.execute(create_table)
    cursor.close()
    conn.close()
    print("altered new table")

if __name__ == '__main__':
    # creat_table()
    alter_table_openalpr()