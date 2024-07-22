import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
from api.v1.routes.auth import auth
from api.v1.models.user import User
from api.db.database import get_db

app = FastAPI()
app.include_router(auth)

# Mock database dependency
def override_get_db():
    db = Mock()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module")
def mock_db():
    return Mock()

@pytest.mark.anyio
async def test_password_reset_email(client, mock_db):
    # Mock user in the database
    test_user = User(email="gihxdma356@couldmail.com", password="fakeha@#23shedpassword")
    mock_db.query.return_value.filter.return_value.first.return_value = test_user

    # Override get_db dependency with mock_db
    app.dependency_overrides[get_db] = lambda: mock_db

    # Determine the correct import path for create_access_token
    with patch('api.v1.routes.auth.reset_password_request', return_value=True) as mock_create_token:
        # Mock the send_password_reset_email function
        # Test valid user
        response = await client.post("/api/v1/auth/reset-password",
                                    json={"new_password": "fakeha@#23shedpassword"},
                                    headers = {
                                        'accept': 'application/json',
                                        'x-reset-token': 'fake_token',
                                        'Content-Type': 'application/json',
                                    })      

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        print(f"create_access_token called: {mock_create_token.called}")

        assert response.status_code == 200

        # Test non-existent user
        response = await client.post("/api/v1/auth/reset-password",
                                    json={"new_password": "fakeha@#23shedpassword"},
                                   )      
        assert response.status_code == 401

       