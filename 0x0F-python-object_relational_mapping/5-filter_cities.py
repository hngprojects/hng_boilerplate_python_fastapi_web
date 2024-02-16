#!/usr/bin/python3
"""
script that lists all cities from the database hbtn_0e_4_usa with states
given as argument
"""
import MySQLdb
import sys

if __name__ == '__main__':
    username, password, database, state_name = sys.argv[1:]
    db = MySQLdb.connect(host="localhost", user=username, port=3306,
                         passwd="Njenga008!", db=database)

    cur = db.cursor()

    cur.execute("""
                SELECT cities.name FROM cities
                INNER JOIN states ON cities.state_id = states.id
                WHERE states.name=%s ORDER BY cities.id ASC""", (state_name,))

    rows = cur.fetchall()

    cities = list(row[0] for row in rows)

    print(*cities, sep=", ")
    cur.close()
    db.close()
