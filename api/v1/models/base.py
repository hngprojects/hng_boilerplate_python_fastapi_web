#!/usr/bin/env python3
""" Base
"""
from sqlalchemy import (
        Column,
        Integer,
        ForeignKey,
        Table
        )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()

user_organisation_association = Table('user_organisation', Base.metadata,
        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
        Column('organisation_id', Integer, ForeignKey('organisations.id'), primary_key=True)
        )
