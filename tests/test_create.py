from sqlalchemy.orm import Session
from ..api.db.database import get_db
# from hng_boilerplate_python_fastapi_web import api
import pytest
from fastapi.testclient import TestClient
from ..main import app



# db.database.get_db
@pytest.fixture(scope='module')
def setUp():
    yield Session(get_db())
    # yield True

@pytest.fixture(scope='module')
def getClient():
    client = TestClient(app)
    yield client
    # yield True

def test_create_product(setUp, getClient):
    client = TestClient(app)
    # print(get_db())
    url = 'http://localhost:7001/api/v1/product/create/'
    
    data = {'name': 'test1', 'description': "thinking", "price": 100, "tags": 'th', }

    response = getClient.post("/api/v1/product/create/", json=data)
    print(response.text)
    
    assert response.status_code == 200

