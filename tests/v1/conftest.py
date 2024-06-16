from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from main import app
from decouple import config
import json


from api.db.database import get_db
from api.db.database import Base
from api.v1.services.auth import User
from api.v1.models.auth import User as UserModel


DB_TYPE = config("DB_TYPE")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
MYSQL_DRIVER = config("MYSQL_DRIVER")
DATABASE_URL = ""

SQLALCHEMY_DATABASE_URL = f'{DB_TYPE}+{MYSQL_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():

        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    payload = {
    "first_name": "dean",
    "last_name": "smith",
    "email": "dean@gmail.com",
    "password": "password123",
    "unique_id": "1005"
}
    res = client.post("/signup/", data=json.dumps(payload))

    assert res.status_code == 201

    new_user = res.json()['data']
    new_user['access_token'] = res.json()['access_token']
    new_user['email'] = payload['email']
    return new_user



