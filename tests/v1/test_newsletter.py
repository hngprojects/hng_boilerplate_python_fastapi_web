import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from ...main import app
from api.db.database import get_db
from api.v1.schemas.newsletter_schema import EMAILSCHEMA
from api.v1.models.newsletter import NEWSLETTER

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(mocker, db_session_mock):
    mocker.patch("app.routes.newsletter_router.get_db", return_value=db_session_mock)

def test_sub_newsletter_success(db_session_mock):
    # Arrange
    db_session_mock.query(NEWSLETTER).filter().first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    email_data = {"email": "test@example.com"}

    # Act
    response = client.post("/api/v1/pages/newsletter", json=email_data)

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "message": "Thank you for subscribing to our newsletter.",
        "success": True,
        "status": 201
    }

def test_sub_newsletter_existing_email(db_session_mock):
    # Arrange
    existing_subscriber = NEWSLETTER(email="test@example.com")
    db_session_mock.query(NEWSLETTER).filter().first.return_value = existing_subscriber

    email_data = {"email": "test@example.com"}

    # Act
    response = client.post("/api/v1/pages/newsletter", json=email_data)

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Email already exists"
    }

if __name__ == "__main__":
    pytest.main()