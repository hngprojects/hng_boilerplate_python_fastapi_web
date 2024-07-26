import sys, os
import warnings
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from main import app
from api.db.database import get_db, Base

from api.utils.settings import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_TYPE = settings.DB_TYPE

# Database setup for testing
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client


@pytest.mark.auth
def test_register(test_client):
    payload = {
        "username": "Skibo",
        "first_name": "Julius",
        "last_name": "Yonwatode",
        "email": "juliusyonwatade@gmail.com",
        "password": "Jayboy99%$"
    }
    response = test_client.post("/auth/register/", json=payload)
    response_json = response.json()
    assert response.status_code == 201

    email = {
        "email": "juliusyonwatade@gmail.com"
    }
    response = test_client.post(f"/auth/password-reset-email/", json=email)
    response_json = response.json()
    assert response.status_code == 200
    assert "reset_link" in response_json
    assert "message" in response_json

@pytest.mark.auth
def test_send_email_failure(test_client):
    email = {"email": "yonwatodejulius@gmail.com"}
    response = test_client.post("/auth/password-reset-email/", json=email)
    response_json = response.json()
    print(response_json)
    assert response.status_code == 200
    assert "message" in response_json

if __name__ == "__main__":
    pytest.main()
