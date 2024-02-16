#!/usr/bin/python3
"""
script that lists all cities from the database hbtn_0e_4_usa
"""
import MySQLdb
import sys

if __name__ == '__main__':
    username, password, database = sys.argv[1:]

    db = MySQLdb.connect(host="localhost", user=username, port=3306,
                         passwd="Njenga008!", db=database)

    cur = db.cursor()

    cur.execute('''
        SELECT cities.id, cities.name, states.name
        FROM cities
        LEFT JOIN states ON cities.state_id = states.id
        ORDER BY cities.id
        ''')

    tuples = cur.fetchall()

    for tup in tuples:
        print(tup)
    cur.close()
    db.close()
