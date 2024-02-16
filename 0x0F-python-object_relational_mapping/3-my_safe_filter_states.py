#!/usr/bin/python3
"""
one that is safe from MySQL injections!
"""


import MySQLdb
import sys

if __name__ == '__main__':
    username, password, database, statename = sys.argv[1:]

    statename = statename.split(' ')[0]

    db = MySQLdb.connect(host="localhost", user=username,
                         passwd="Njenga008!", db=database)

    cur = db.cursor()

    query = "SELECT * FROM states WHERE name LIKE BINARY %s ORDER BY id"

    cur.execute(query, (statename,))

    rows = cur.fetchall()

    for row in rows:
        print(row)
