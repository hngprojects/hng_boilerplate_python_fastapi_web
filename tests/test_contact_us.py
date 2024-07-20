from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

def test_contact_us_success(monkeypatch):
    def mock_send_email_via_service(name, email, message):
        return True
    monkeypatch.setattr("api.v1.routes.contact_us.send_email_via_service", mock_send_email_via_service)
    response = client.post("/api/v1/contact", json={
        "name": "Test",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Inquiry sent successfully", "status": 200}

def test_contact_us_failure(monkeypatch):
    def mock_send_email_via_service(name, email, message):
        return False
    monkeypatch.setattr("api.v1.routes.contact_us.send_email_via_service", mock_send_email_via_service)
    response = client.post("/api/v1/contact", json={
        "name": "Test",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to send inquiry"}

def test_contact_us_invalid_email():
    response = client.post("/api/v1/contact", json={
        "name": "Test",
        "email": "invalid-email",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 422

def test_contact_us_missing_fields():
    response = client.post("/api/v1/contact", json={
        "name": "Test",
        "email": "test@example.com",
        "message": "Hello, this is a test message."
    })
    assert response.status_code == 422

def test_contact_us_empty_message():
    response = client.post("/api/v1/contact", json={
        "name": "Test",
        "email": "test@example.com",
        "message": ""
    })
    assert response.status_code == 422
