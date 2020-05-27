import sqlite3
import time
import os
import re 


def search_mytb():
    conn = sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    sql = '''
    insert into mytb(comment, tdate)
    values
    (?,?)'''

    cursor.execute(sql, (comm, tdata))
    conn.comit()
    cursor.close
    conn.close()
    print("insert data.")

import subprocess 
def test_openalpr():
    # txt = os.system("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu MY02ZR0.jpg | sed -n '2p'"))
    res = subprocess.getstatusoutput("docker run -it --rm -v $(pwd):/data:ro openalpr -c eu MY02ZR0.jpg | sed -n '2p'")
    print(res)
    record = res[1].split("\t confidence: ")
    print(record)
    # return plate_str, confidence     
    return record[0], record[1]



def insert_data(id, plate, score, time):
    conn = sqlite3.connect('./mydata.db')
    cursor = conn.cursor()
    # print(record[0])
    cursor.execute("INSERT INTO OPENALPR (ID, PLATE,SCORE,TIME) \
      VALUES (?, ?, ?, ? )", (id, plate, score, time))
    conn.commit()
    cursor.close
    conn.close()
    print("Inserted data.")


if __name__ == "__main__":
    start_time = time.time()
    plate, score = test_openalpr()
    stop_time = time.time()
    insert_data(2, "MYO2ZRD", "90.1", str(stop_time - start_time))

    # - MYO2ZRD	 confidence: 93.2684