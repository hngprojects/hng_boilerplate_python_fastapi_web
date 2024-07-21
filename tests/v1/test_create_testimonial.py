#!/usr/bin/env python3
"""
Pytest
Test case for creating a Testimonial
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from api.utils.auth import hash_password

client = TestClient(app)

@pytest.fixture
def mock_db():
    """
    Create a mock database session
    """
    mock_session = MagicMock()
    yield mock_session

def test_create_testimonial_success(mock_db, mocker):
    """
    Mock get_current_user
    """
    mock_user = {"id": 1, "username": "testuser"}
    mocker.patch("api.utils.dependencies.get_current_user", return_value=mock_user)


    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    mock_testimonial = MagicMock()
    mock_testimonial.id = 1
    mock_testimonial.firstname = "John"
    mock_testimonial.lastname = "Doe"
    mock_testimonial.content = "This is a great service!"
    mock_testimonial.created_at = "2024-07-21T00:00:00Z"
    mock_testimonial.updated_at = "2024-07-21T00:00:00Z"

    mocker.patch("api.v1.models.testimonial.Testimonial", return_value=mock_testimonial)

    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    access_token = response.json().get("access_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    testimonial_data = {
        "firstname": "John",
        "lastname": "Doe",
        "content": "This is a great service!"
    }

    response = client.post("/api/v1/testimonials", json=testimonial_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Testimonial created successfully"
    assert response.json()["data"]["firstname"] == "John"
    assert response.json()["data"]["lastname"] == "Doe"
    assert response.json()["data"]["content"] == "This is a great service!"

def test_create_testimonial_unauthenticated():
    testimonial_data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "content": "Amazing experience!"
    }

    response = client.post("/api/v1/testimonials", json=testimonial_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


