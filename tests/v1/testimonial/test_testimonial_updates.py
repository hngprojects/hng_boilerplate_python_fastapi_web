import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone
from faker import Faker
from main import app
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from api.v1.services.user import user_service
from fastapi import status

fake = Faker()
client = TestClient(app)

# Fixtures
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    return db_session

@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def mock_get_current_user():
    return User(
        id=str(uuid7()),
        email=fake.email(),
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

def mock_testimonial(user_id):
    return Testimonial(
        id=str(uuid7()),
        content="Original content",
        author_id=user_id,  
        client_name="Client 1",
        client_designation="Client Designation",
        comments="Testimonial comments",
        ratings=4.5
    )


def test_update_testimonial_success(client, db_session_mock):
    '''Test successful update of a testimonial'''
    
    mock_user = mock_get_current_user()
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_user
    
    mock_testimonial_obj = mock_testimonial(mock_user.id)
    db_session_mock.get.return_value = mock_testimonial_obj
    
    update_data = {"content": "Updated content"}
    response = client.put(
        f'/api/v1/testimonials/{mock_testimonial_obj.id}',
        json=update_data,
        headers={'Authorization': 'Bearer token'}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Testimonial updated successfully"


def test_update_testimonial_not_found(client, db_session_mock):
    '''Test updating a non-existing testimonial'''
    
    app.dependency_overrides[user_service.get_current_user] = lambda: mock_get_current_user()
    
    db_session_mock.get.return_value = None
    
    update_data = {"content": "Updated content"}
    testimonial_id = str(uuid7())
    response = client.put(
        f'/api/v1/testimonials/{testimonial_id}',
        json=update_data,
        headers={'Authorization': 'Bearer token'}
        )
    
    assert response.status_code == 404
    assert response.json()["message"] in ["Testimonial not found", "Testimonial does not exist"]

def test_update_testimonial_unauthorized(client):
    '''Test updating a testimonial without authentication'''
    
    testimonial_id = str(uuid7())
    update_data = {"content": "Updated content"}
    
    response = client.put(f'/api/v1/testimonials/{testimonial_id}', json=update_data)
    
    assert response.status_code == 401
    assert response.json()["message"] == "Not authenticated"
