#!/usr/bin/python3
"""
Script that lists all states with a name starting with N from the
database hbtn_0e_0_usa.
"""
import MySQLdb
import sys


if __name__ == "__main__":
    username, password, database = sys.argv[1:]
    db = MySQLdb.connect(host='localhost', port=3306, user=username,
                         passwd='Njenga008!', db=database)

    cur = db.cursor()
    cur.execute("SELECT * FROM states WHERE name LIKE BINARY 'N%' ORDER BY id")
    statess = cur.fetchall()

    cur.close()
    db.close()
    for state in statess:
        print(state)
