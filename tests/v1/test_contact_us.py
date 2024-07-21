from fastapi.testclient import TestClient
import pytest
from ...main import app

# Assuming the email service is defined in services.email_service
from api.v1.routes.contact_us import EmailService

client = TestClient(app)


class MockEmailServiceSuccess:
    def send_email(self, name: str, email: str, message: str) -> bool:
                    return True


class MockEmailServiceFailure:
    def send_email(self, name: str, email: str, message: str) -> bool:
        return False


@pytest.fixture
def mock_email_service_success():
    app.dependency_overrides[EmailService] = lambda: MockEmailServiceSuccess()
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_email_service_failure():
    app.dependency_overrides[EmailService] = lambda: MockEmailServiceFailure()
    yield
    app.dependency_overrides = {}


def test_contact_us_success(mock_email_service_success):
    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Inquiry sent successfully", "status": 200}


def test_contact_us_failure(mock_email_service_failure):
    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to send inquiry"}


def test_contact_us_invalid_email():
    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "invalid-email",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 422


def test_contact_us_missing_fields():
    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "test@example.com"
    })
    assert response.status_code == 422


def test_contact_us_empty_message():
    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": ""
    })
    assert response.status_code == 422


def test_contact_us_missing_name():
    response = client.post("/api/v1/contact", json={
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 422
    assert "name" in response.json()["detail"][0]["loc"]


def test_contact_us_excessive_length():
    long_string = "a" * 1001
    response = client.post("/api/v1/contact", json={
        "name": long_string,
        "email": "test@example.com",
        "message": long_string
    })
    assert response.status_code == 422


def test_contact_us_max_length_exceeded():
    exceed_name = "a" * 51
    exceed_email = "a" * 95 + "@test.com"
    exceed_message = "a" * 1001
    response = client.post("/api/v1/contact", json={
        "name": exceed_name,
        "email": exceed_email,
        "message": exceed_message
    })
    assert response.status_code == 422


def test_contact_us_special_characters_in_name():
    response = client.post("/api/v1/contact", json={
        "name": "@#$%^&*()",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 200


def test_contact_us_script_in_message():
    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": "<script>alert('XSS')</script>"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Inquiry sent successfully", "status": 200}
