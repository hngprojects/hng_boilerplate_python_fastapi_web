#!/usr/bin/python3
""" Define State model """
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()


class State(Base):
    """ Define a class State to be linked to db table """
    __tablename__ = 'states'

    id = Column(Integer, nullable=False,
                autoincrement=True, unique=True,
                primary_key=True)
    name = Column(String(128), nullable=False)
