import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from main import app
from api.db.database import get_db, get_db_engine, Base

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


    testimonial_data = {
        "content_data" : "I love testimonials"
    }
    response = client.put(f'/api/v1/testimonials/{testimonial_id}', json=testimonial_data)

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
 




 
  