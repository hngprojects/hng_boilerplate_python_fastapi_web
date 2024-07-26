import pytest
from httpx import AsyncClient
from api.main import app
from api.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_activity_log(client, test_db):
    response = await client.post(
        "/api/v1/activity-logs/create",
        headers={"Authorization": "Bearer YOUR_TEST_TOKEN_HERE"},
        json={
            "user_id": "0669ff22-1394-7a89-8000-4b619aebb477",
            "action": "Logged in",
            "description": "User logged in for testing"
        },
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Activity log created successfully"

