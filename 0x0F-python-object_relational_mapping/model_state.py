#!/usr/bin/python3
"""Defines a State class and creates an instance Base = declarative_base()"""
import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class State(Base):
    """Represents a state"""
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True)
    name =  Column(String(128), nullable=False)
