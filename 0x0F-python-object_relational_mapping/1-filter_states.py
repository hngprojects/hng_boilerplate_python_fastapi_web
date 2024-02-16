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

    cursor = db.cursor()
    query = "SELECT id, name FROM (SELECT name, MIN(id) AS id FROM states "
    queryext = "WHERE name LIKE 'N%' GROUP BY name) AS t ORDER BY id;"
    q = query + queryext
    cursor.execute(q)
    statess = cursor.fetchall()

    cursor.close()
    db.close()


    for state in statess:
            print(state)
