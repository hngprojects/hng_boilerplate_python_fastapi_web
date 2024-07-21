from fastapi.testclient import TestClient
import pytest
from main import app

# Assuming the email service is defined in services.email_service
from services.email_service import EmailService

client = TestClient(app)


class MockEmailServiceSuccess:
    def send_email(self, name: str, email: str, message: str) -> bool:
        return True


class MockEmailServiceFailure:
    def send_email(self, name: str, email: str, message: str) -> bool:
        return False


def test_contact_us_success(monkeypatch):
    def mock_dependency():
        return MockEmailServiceSuccess()
    monkeypatch.setattr("api.v1.routes.contact_us.Depends", mock_dependency)

    response = client.post("/api/v1/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Inquiry sent successfully", "status": 200}


def test_contact_us_failure(monkeypatch):
    def mock_dependency():
        return MockEmailServiceFailure()
    monkeypatch.setattr("api.v1.routes.contact_us.Depends", mock_dependency)

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
