import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
from api.v1.routes import members
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.base import user_organization_association
from api.db.database import get_db

app = FastAPI()
app.include_router(members.router)

# Mock data
mock_users = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "user1",
        "email": "user1@example.com",
        "password": "hashed_password1",
        "first_name": "First1",
        "last_name": "Last1",
        "created_at": "2024-07-20 21:21:03.328973+03",
        "updated_at": "2024-07-20 21:21:03.328973+03"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "user2",
        "email": "user2@example.com",
        "password": "hashed_password2",
        "first_name": "First2",
        "last_name": "Last2",
        "created_at": "2024-07-20 21:21:03.328973+03",
        "updated_at": "2024-07-20 21:21:03.328973+03"
    }
]

mock_organizations = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Organization 1",
        "description": "Description 1",
        "created_at": "2024-07-20 21:19:51.5209+03",
        "updated_at": "2024-07-20 21:19:51.5209+03"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Organization 2",
        "description": "Description 2",
        "created_at": "2024-07-20 21:19:51.5209+03",
        "updated_at": "2024-07-20 21:19:51.5209+03"
    }
]

mock_user_organization = [
    {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "organization_id": "550e8400-e29b-41d4-a716-446655440001",
        "status": "members"
    },
    {
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "organization_id": "550e8400-e29b-41d4-a716-446655440002",
        "status": "suspended"
    }
]

# Mock the database dependency
def override_get_db():
    db = Mock()
    db.query.side_effect = lambda model: {
        User: mock_users,
        Organization: mock_organizations,
        user_organization_association: mock_user_organization
    }.get(model, [])
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

@patch("api.db.database.get_db", new_callable=override_get_db)
async def test_get_members(mock_session, client):
    organization_id = "550e8400-e29b-41d4-a716-446655440001"
    status = "members"
    page = 1
    limit = 10
    response = await client.get(f"/api/v1/organizations/{organization_id}/members?status={status}&page={page}&limit={limit}")

    assert response.status_code == 200
    assert response.json() == {
        "total": 1,
        "page": 1,
        "limit": 10,
        "prev": None,
        "next": None,
        "users": [
            {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_email": "user1@example.com",
                "organization_name": "Organization 1"
            }
        ]
    }
