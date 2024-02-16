#!/usr/bin/python3
import MySQLdb
import sys
import sqlalchemy
def list_states(username, password, database):
    db = MySQLdb.connect(host='localhost', user=username, passwd='Njenga008!', db=database)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM states ORDER BY id ASC")

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    db.close()

if __name__ == "__main__":
    username, password, database = sys.argv[1:]

    list_states(username, password, database)
