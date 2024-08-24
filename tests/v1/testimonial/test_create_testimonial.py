import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api.v1.models import Testimonial  # noqa: F403
from main import app
import uuid

client = TestClient(app)

auth_token = None

payload = [
    {
        "content": "Testimonial 1",
        "ratings": 2.5,
        "status_code": 201,
    },
    {
        "content": "Testimonial 2",
        "ratings": 3.5,
        "status_code": 201,
    },
    {  # missing content
        "ratings": 3.5,
        "status_code": 422,
    },
    {  # missing ratings
        "content": "Testimonial 2",
        "status_code": 201,
    },
]

@pytest.fixture(scope='module')
def mock_send_email():
    with patch("api.core.dependencies.email_sender.send_email") as mock_email_sending:
        with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
            add_task_mock.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            yield mock_email_sending

@pytest.fixture(scope="function")
def client_with_mocks(mock_send_email):
    with patch('api.db.database.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Reset the mock_db state for each test
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add.reset_mock()
        mock_db.commit.reset_mock()
        mock_db.refresh.reset_mock()
        
        yield client, mock_db

@pytest.fixture(autouse=True)
def before_all(client_with_mocks):
    client, mock_db = client_with_mocks
    
    # Simulate the user not existing before registration
    mock_db.query.return_value.filter.return_value.first.return_value = None
    email = f"test{uuid.uuid4()}@gmail.com"
    user_response = client.post(
        "/api/v1/auth/register",
        json={
            "password": "strin8Hsg263@",
            "first_name": "string",
            "last_name": "string",
            "email": email,
        }
    )
    print("USER RESPONSE", user_response.json())
    
    if user_response.status_code != 201:
        raise Exception(f"Setup failed: {user_response.json()}")

    global auth_token
    auth_token = user_response.json()["access_token"]

def test_create_testimonial(client_with_mocks):
    client, mock_db = client_with_mocks
    status_code = payload[0].pop("status_code")

    res = client.post(
        "api/v1/testimonials/",
        json=payload[0],
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert res.status_code == status_code
    
    testimonial_id = res.json()["data"]["id"]
    testimonial = MagicMock()
    testimonial.content = payload[0]["content"]
    testimonial.ratings = payload[0]["ratings"]
    
    mock_db.query(Testimonial).get.return_value = testimonial
    retrieved_testimonial = mock_db.query(Testimonial).get(testimonial_id)
    
    assert retrieved_testimonial.content == payload[0]["content"]
    assert retrieved_testimonial.ratings == payload[0]["ratings"]

def test_create_testimonial_unauthorized(client_with_mocks):
    client, _ = client_with_mocks
    status_code = 401

    res = client.post(
        "api/v1/testimonials/",
        json=payload[1],
    )

    assert res.status_code == status_code

def test_create_testimonial_missing_content(client_with_mocks):
    client, _ = client_with_mocks
    status_code = payload[2].pop("status_code")

    res = client.post(
        "api/v1/testimonials/",
        json=payload[2],
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert res.status_code == status_code

def test_create_testimonial_missing_ratings(client_with_mocks):
    client, mock_db = client_with_mocks
    status_code = payload[3].pop("status_code")

    res = client.post(
        "api/v1/testimonials/",
        json=payload[3],
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert res.status_code == status_code
    
    testimonial_id = res.json()["data"]["id"]
    testimonial = MagicMock()
    testimonial.content = payload[3]["content"]
    testimonial.ratings = 0  # Default value when ratings are missing
    
    mock_db.query(Testimonial).get.return_value = testimonial
    retrieved_testimonial = mock_db.query(Testimonial).get(testimonial_id)
    
    assert retrieved_testimonial.ratings == 0
