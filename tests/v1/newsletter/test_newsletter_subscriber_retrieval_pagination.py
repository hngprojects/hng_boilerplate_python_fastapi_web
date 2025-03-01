from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.v1.models.newsletter import NewsletterSubscriber
from api.v1.services.newsletter import NewsletterService
from main import app
from faker import Faker

fake = Faker()

def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_newsletter_subscriber():
    return NewsletterSubscriber(
        id=str(uuid7()),
        email=fake.email(),
        created_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_get_subscribers_success(client, db_session_mock):
    '''Test to successfully retrieve newsletter subscribers'''
    
    # Mock the admin user
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    
    # Mock newsletter service response
    mock_paginated_result = {
        "subscribers": [mock_newsletter_subscriber()],
        "page": 1,
        "per_page": 10,
        "total_subscribers": 1,
        "total_pages": 1
    }

    with patch("api.v1.services.newsletter.NewsletterService.get_paginated_subscribers", 
               return_value=mock_paginated_result):
        response = client.get(
            '/api/v1/newsletters/subscribers',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Subscriptions retrieved successfully"
        assert "subscribers" in response.json()["data"]

def test_get_subscribers_unauthorized(client, db_session_mock):
    '''Test for unauthorized access'''
    
    response = client.get(
        '/api/v1/newsletters/subscribers'
    )

    assert response.status_code == 401

def test_get_subscribers_empty_list(client, db_session_mock):
    '''Test when no subscribers exist'''
    
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin
    
    mock_empty_result = {
        "subscribers": [],
        "page": 1,
        "per_page": 10,
        "total_subscribers": 0,
        "total_pages": 0
    }

    with patch("api.v1.services.newsletter.NewsletterService.get_paginated_subscribers", 
               return_value=mock_empty_result):
        response = client.get(
            '/api/v1/newsletters/subscribers',
            headers={'Authorization': 'Bearer token'}
        )

        assert response.status_code == 200
        assert response.json()["data"]["subscribers"] == [{}]
