#!/usr/bin/python3
"""
Script that lists all states with a name starting with N from the
database hbtn_0e_0_usa.
"""
import MySQLdb
import sys


def filter_by_n(username, password, database):
    """
    Connects to the MySQL server, retrieves states whose names start with 'N'.
    Args:
        username (str): MySQL username.
        password (str): MySQL password.
        database (str): MySQL database name.

    Returns:
        list: List of tuples containing the state data.
    """
    try:
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

    except MySQLdb.Error as e:
        print("MySQL Error:", e)

    if statess:
        for state in statess:
            print(state)


if __name__ == "__main__":
    username, password, database = sys.argv[1:]
    filter_by_n(username, password, database)
