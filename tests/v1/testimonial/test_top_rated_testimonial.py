import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from api.db.database import get_db
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def db_session_mock():
    """Mock database session"""
    return MagicMock()

@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock
    
    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}

def test_get_top_rated_api(db_session_mock):
    """Test the /top-rated API endpoint"""
    mock_testimonial = MagicMock()
    mock_testimonial.id = "123"
    mock_testimonial.content = "Excellent service!"
    mock_testimonial.ratings = 5.0
    mock_testimonial.author_id = "abc"
    mock_testimonial.created_at = datetime.now()

    db_session_mock.query().order_by().offset().limit().all.return_value = [mock_testimonial]
    
    response = client.get("/api/v1/testimonials/top-rated", params={"page": 1, "per_page": 1})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Top-rated testimonials retrieved successfully."
    assert len(response.json()["data"]) == 1

def test_no_testimonials(db_session_mock):
    """Test for when no testimonials exist in the database"""
    db_session_mock.query().order_by().offset().limit().all.return_value = []

    response = client.get("/api/v1/testimonials/top-rated", params={"page": 1, "per_page": 10})

    assert response.status_code == 200
    assert response.json()["message"] == "No testimonials found."
    assert response.json()["data"] == []

@pytest.mark.parametrize("page, per_page", [(0, 10),  (-1, 10), (1, 0), (1, -5)])
def test_invalid_pagination_params(page, per_page):
    """Test for invalid pagination"""
    response = client.get("/api/v1/testimonials/top-rated", params={"page": page, "per_page": per_page})

    assert response.status_code == 422