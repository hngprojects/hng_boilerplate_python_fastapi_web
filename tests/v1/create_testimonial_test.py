import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from main import app
from api.v1.models.testimonial import Testimonial
from api.v1.models.user import User
from api.v1.routes.testimonial import get_db
from api.v1.schemas.testimonial_schema import TestimonialCreate

# Mock database dependency
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

def test_create_testimonial(client, db_session_mock):
    user_id = str(uuid7())
    testimonial_id = str(uuid7())
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    created_at = timeinfo
    updated_at = timeinfo

    # Create a mock user
    user = User(id=user_id, username="testuser", email="testuser@example.com")

    # Data for creating a testimonial
    testimonial_data = {
        "content": "This is a test testimonial",
        "client_designation": "Client Designation",
        "client_name": "Client Name",
        "ratings": 4.5
    }

    # Mock the return value for the query to get the current user
    with patch('api.v1.services.user.user_service.get_current_user', return_value=user):
        # Call the endpoint
        response = client.post("/api/v1/testimonials", json=testimonial_data)

    # Mock the return value for the query to get testimonials
    testimonial = Testimonial(
        id=testimonial_id,
        content=testimonial_data["content"],
        client_designation=testimonial_data["client_designation"],
        client_name=testimonial_data["client_name"],
        ratings=testimonial_data["ratings"],
        author_id=user_id,
        created_at=created_at,
        updated_at=updated_at
    )

    db_session_mock.query().filter().first.return_value = testimonial

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"] == testimonial_data["content"]
    assert response_data["client_designation"] == testimonial_data["client_designation"]
    assert response_data["client_name"] == testimonial_data["client_name"]
    assert response_data["ratings"] == testimonial_data["ratings"]
    assert response_data["author_id"] == user_id
