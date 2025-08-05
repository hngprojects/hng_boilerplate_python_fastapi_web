import pytest
from main import app
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from api.db.database import get_db
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.v1.services.testimonial import testimonial_service, TestimonialService
from api.v1.services.user import user_service
from api.v1.models import User, Testimonial

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock

@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as user_service_mock:
        yield user_service_mock



@pytest.fixture
def mock_testimonial_service(mock_db_session):
    with patch("api.v1.services.testimonial.TestimonialService", autospec=True) as mock_testimonial_service:
        yield mock_testimonial_service(mock_db_session)


# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )

@pytest.fixture()
def test_testimonial(test_user):
    return Testimonial(
        id=str(uuid7()),
        content= "Testimonial 1",
        ratings=2.5,
    )



@pytest.fixture
def access_token_user(test_user):
    return user_service.create_access_token(user_id=test_user.id)



@patch("api.v1.services.testimonial.TestimonialService.create")
def test_successful_testimonial(
    mock_create_testimonial,
    mock_db_session, 
    test_user, 
    test_testimonial,
    access_token_user
):
    # mock current-user AND blog-post
    mock_db_session.query().filter().first.side_effect = [test_user, test_testimonial]

    # mock existing-blog-like
    mock_db_session.query().filter_by().first.return_value = None

    # mock like-count
    mock_db_session.query().filter_by().count.return_value = 1

    resp = client.post(
        f"api/v1/testimonials/",
        headers={"Authorization": f"Bearer {access_token_user}"},
        json={
        "content": "Testimonial 1",
        "ratings": 2.5
        }
    )
    resp_d = resp.json()
    assert resp.status_code == 201

@patch("api.v1.services.testimonial.TestimonialService.create")
def test_unauthorized_testimonial(
    mock_create_testimonial,
    mock_db_session, 
    test_user, 
    test_testimonial,
):
    # mock current-user AND blog-post
    mock_db_session.query().filter().first.side_effect = [test_user, test_testimonial]

    # mock existing-blog-like
    mock_db_session.query().filter_by().first.return_value = None

    # mock like-count
    mock_db_session.query().filter_by().count.return_value = 1

    resp = client.post(
        f"api/v1/testimonials/",
        json={
        "content": "Testimonial 1",
        "ratings": 2.5
        }
    )
    resp_d = resp.json()
    assert resp.status_code == 401


@patch("api.v1.services.testimonial.TestimonialService.create")
def test_missing_content_testimonial(
    mock_create_testimonial,
    mock_db_session, 
    test_user, 
    test_testimonial,
    access_token_user
):
    # mock current-user AND blog-post
    mock_db_session.query().filter().first.side_effect = [test_user, test_testimonial]

    # mock existing-blog-like
    mock_db_session.query().filter_by().first.return_value = None

    # mock like-count
    mock_db_session.query().filter_by().count.return_value = 1

    resp = client.post(
        f"api/v1/testimonials/",
        headers={"Authorization": f"Bearer {access_token_user}"},
        json={
        "ratings": 2.5
        }
    )
    resp_d = resp.json()
    assert resp.status_code == 422


@patch("api.v1.services.testimonial.TestimonialService.create")
def test_missing_ratings_testimonial(
    mock_create_testimonial,
    mock_db_session, 
    test_user, 
    test_testimonial,
    access_token_user
):
    # mock current-user AND blog-post
    mock_db_session.query().filter().first.side_effect = [test_user, test_testimonial]

    # mock existing-blog-like
    mock_db_session.query().filter_by().first.return_value = None

    # mock like-count
    mock_db_session.query().filter_by().count.return_value = 1

    resp = client.post(
        f"api/v1/testimonials/",
        headers={"Authorization": f"Bearer {access_token_user}"},
        json={
        "content": "Testimonial 1",
        }
    )
    resp_d = resp.json()
    assert resp.status_code == 201
    
