import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base
from api.v1.main import app  # Adjust the import to your main FastAPI app
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.schemas.invitations import InvitationCreate

# Create a test database engine
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:golden@localhost:5432/HNG4test"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_session dependency for testing
def override_get_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_session

# Create tables in the test database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


def setup_test_data(db_session):
    user = User(id=1, name="Test User", email="testuser@example.com")
    org = Organization(id=1, name="Test Organization")
    db_session.add(user)
    db_session.add(org)
    db_session.commit()


@pytest.mark.asyncio
async def test_generate_invite_link(client, db_session):
    setup_test_data(db_session)

    invite_data = {
        "user_id": 1,
        "organization_id": 1
    }

    response = await client.post("/api/v1/invite/create", json=invite_data)

    assert response.status_code == 200
    response_data = response.json()
    assert "invitation_link" in response_data
    assert response_data["invitation_link"].startswith("http://127.0.0.1:8000/api/v1/invite/accept?invitation_id=")
