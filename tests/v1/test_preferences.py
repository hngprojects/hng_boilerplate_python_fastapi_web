from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_preference():
    response = client.post(
        "/api/v1/1/preference",
        json={"key": "test_key", "value": "test_value"}
    )
    assert response.status_code == 200
    assert response.json()["key"] == "test_key"
