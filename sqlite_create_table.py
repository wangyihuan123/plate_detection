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

if __name__ == '__main__':
    creat_table()