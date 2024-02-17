#!/usr/bin/python3
"""
lists all State objects, and corresponding City objects, contained in
the database hbtn_0e_101_usa
"""

import sqlalchemy
from sqlalchemy import create_engine, text
from relationship_state import Base, State
import sys
from relationship_city import City
from sqlalchemy.orm import sessionmaker, relationship

if __name__ == '__main__':
    engine = create_engine('mysql+mysqldb://{}:{}@localhost/{}'.
                           format(sys.argv[1], sys.argv[2], sys.argv[
                               3], pool_pre_ping=True))

    Session = sessionmaker(engine)

    session = Session()

    states = session.query(State).order_by(State.id).all()

    for state in states:
        print("{}: {}".format(state.id, state.name))
        for city in state.cities:
            print("\t{}: {}".format(city.id, city.name))
    session.close()
