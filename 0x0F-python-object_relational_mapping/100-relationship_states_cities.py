#!/usr/bin/python3
"""Creates a new state and inserts it into the database"""


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

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(engine)

    session = Session()

    new = State(name='California')
    new_city = City(name='San Francisco')

    new.cities.append(new_city)

    session.add(new)
    session.add(new_city)
    session.commit()
