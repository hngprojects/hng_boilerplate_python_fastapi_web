#!/usr/bin/python3
"""
lists all City objects from the database hbtn_0e_101_usa
"""

import sqlalchemy
from sqlalchemy import create_engine
from relationship_state import Base, State
import sys
from relationship_city import City
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
    engine = create_engine('mysql+mysqldb://{}:{}@localhost/{}'.
                           format(sys.argv[1], sys.argv[2], sys.argv[
                               3], pool_pre_ping=True))

    Session = sessionmaker(engine)

    session = Session()

    cities = session.query(City).order_by(City.id).all()

    for city in cities:
        print("{}: {} -> {}".format(city.id, city.name, city.state.name))
    session.close()
