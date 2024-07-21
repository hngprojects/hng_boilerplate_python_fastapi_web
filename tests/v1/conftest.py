# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...main import app
from api.db.database import get_db
from api.v1.models.base import Base
from decouple import config
from api.utils.settings import BASE_DIR


DB_TYPE = config("DB_TYPE")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
MYSQL_DRIVER = config("MYSQL_DRIVER")
DATABASE_URL = ""

SQLALCHEMY_DATABASE_URL = f'{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'
# BASE_PATH = f"sqlite:///{BASE_DIR}"
# SQLALCHEMY_DATABASE_URL = BASE_PATH + "test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    # session.close()
    # transaction.rollback()
    # connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""
    def override_get_db():
        # try:
        yield db_session
        # finally:
            # db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides[get_db] = get_db  # Reset after test

