#!/usr/bin/env python3
""" The database module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
from contextlib import contextmanager
from api.v1.models.base import Base


def get_db_engine():

    DB_TYPE = config("DB_TYPE", "")
    DB_NAME = config("DB_NAME", "")
    DB_USER = config("DB_USER", "")
    DB_PASSWORD = config("DB_PASSWORD", "")
    DB_HOST = config("DB_HOST", "")
    DB_PORT = config("DB_PORT", "")
    MYSQL_DRIVER = config("MYSQL_DRIVER", "")
    DATABASE_URL = ""

    if DB_TYPE == "mysql":
        DATABASE_URL = f'mysql+{MYSQL_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    elif DB_TYPE == "postgresql":
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        DATABASE_URL = "sqlite:///./database.db"

    if DB_TYPE == "sqlite":
        db_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        db_engine = create_engine(DATABASE_URL, pool_size=32, max_overflow=64)
    
    return db_engine

db_engine = get_db_engine()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def create_database():
    return Base.metadata.create_all(bind=db_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
