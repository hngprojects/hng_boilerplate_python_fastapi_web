#!/usr/bin/python3
"""Add therb staet Louisiana
"""
import sys
from model_state import Base, State
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (create_engine)

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

    newstate = State(name="Louisiana")
    session.add(newstate)
    session.commit()

    print(newstate.id)

    session.close()
