# test_newsletter.py
from unittest.mock import MagicMock, patch

import pytest
from api.db.database import get_db
from api.v1.models.newsletter import NewsletterSubscriber
from api.v1.schemas.newsletter import EmailSchema
from api.v1.services.newsletter import NewsletterService
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
# Adjust the import to match your project's structure
from main import app


@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    

@pytest.fixture
def test_email():
    return EmailSchema(email="test@example.com")


@pytest.fixture
def add_test_subscriber(db_session_mock, test_email: EmailSchema):
    test_subscriber = NewsletterService.create(db_session_mock, test_email)
    return test_subscriber



def test_unsubscribe_success(db_session_mock, client: TestClient, add_test_subscriber: EmailSchema):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[NewsletterService.check_nonexisting_subscriber] = lambda: add_test_subscriber

    response = client.post(
                "/api/v1/pages/newsletter/unsubscribe",
                json={"email": add_test_subscriber.email}
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "You have unsubscribed from our newsletter."


def test_unsubscribe_non_existing_email(db_session_mock, client: TestClient):

    db_session_mock.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == "non_existing@example.com").first.return_value = None

    app.dependency_overrides[get_db] = lambda: db_session_mock
    
    app.dependency_overrides[get_db] = lambda: db_session_mock
    app.dependency_overrides[NewsletterService.check_nonexisting_subscriber] = lambda: None

    response = client.post(
        "/api/v1/pages/newsletter/unsubscribe",
        json={"email": "non_existing@example.com"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == "Subscriber not found."

def test_unsubscribe_invalid_email(client: TestClient):
    response = client.post(
        "/api/v1/pages/newsletter/unsubscribe",
        json={"email": "invalid-email-format"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["message"] == "Invalid input"
