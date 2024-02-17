#!/usr/bin/python3
"""lists all city objs from the said database
"""
import sys
from model_state import Base, State
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (create_engine)
from model_city import City

if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    database = sys.argv[3]
    host = 'localhost'
    port = 3306

    db_uri = "mysql://{}:{}@{}:{}/{}".format(username, password, host,
                                             port, database)
    engine = create_engine(db_uri, pool_pre_ping=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    cities = session.query(City, State).filter(City.state_id == State.id)\
        .order_by(City.id.asc()).all()

    for city, state in cities:
        print("{}: ({}) {}".format(state.name, city.id, city.name))

    session.close()
