# api/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Fetch the database URL from the environment variables
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fastuser:password@localhost/hng_fast")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
