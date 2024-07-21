import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from ...main import app
from api.db.database import get_db
from datetime import datetime
from api.v1.schemas.testimonial import TestimonialResponse
from api.v1.models.testimonials import Testimonial

client = TestClient(app)

# Mock the database dependency
@pytest.fixture
def db_session_mock(mocker):
    db_session = mocker.MagicMock()
    yield db_session

# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(mocker, db_session_mock):
    mocker.patch("app.routes.testimonial.get_db", return_value=db_session_mock)

def test_update_testimonial_with_id(db_session_mock, testimonial_id):


    db_session_mock.query(Testimonial).filter(Testimonial.id == testimonial_id).first.return_value = None
    db_session_mock.add.return_value = None
    db_session_mock.commit.return_value = None

    testimonial_data = {
        "content_data" : "I love testimonials"
    }
    response = client.post(f'/api/v1/testimonials/{testimonial_id}', json=testimonial_data)

    assert response.status_code == 200
    assert response.json() == {
          'status' : 200,
          'message' : 'Testimonial Updated Successfully',
          'data': {
               'user_id' : 'random_id',
               'content' : 'I love testimonials',
               'updated_at' : 'cureent_time'
          }
    }


if __name__ == "__main__":
    pytest.main()

 
  