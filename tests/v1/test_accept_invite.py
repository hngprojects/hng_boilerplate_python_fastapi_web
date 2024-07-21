import pytest
import asyncio
import uuid, os
from dotenv import load_dotenv
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.v1.models.invitation import Invitation
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.db.database import Base
from main import app

load_dotenv()

DATABASE_URL = os.environ.get("PSGL_TEST_DB_URI")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_app():
    yield app

@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def create_invitation(db_session):
    def _create_invitation(user_id, organization_id, expires_at=None, is_valid=True):
        expires_at = expires_at or (datetime.utcnow() + timedelta(days=1))
        invitation = Invitation(user_id=user_id, organization_id=organization_id, expires_at=expires_at, is_valid=is_valid)
        db_session.add(invitation)
        db_session.commit()
        db_session.refresh(invitation)
        return invitation
    return _create_invitation

@pytest.fixture(scope="function")
def create_user_and_org(db_session):
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    unique_username = f"test_user_{uuid.uuid4()}"
    unique_email = f"test_user_{uuid.uuid4()}@example.com"
    unique_org_name = f"test_org_{uuid.uuid4()}"
    
    user = User(id=user_id, username=unique_username, email=unique_email, password="test_password")
    org = Organization(id=org_id, name=unique_org_name)
    
    db_session.add(user)
    db_session.add(org)
    db_session.commit()
    
    return user_id, org_id

@pytest.mark.asyncio
async def test_valid_invitation(test_app, create_invitation, create_user_and_org):
    user_id, org_id = create_user_and_org
    invitation = create_invitation(user_id=user_id, organization_id=org_id)

    invitation_link = f"http://test/api/v1/invite/accept?invitation_id={invitation.id}"

    async with AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.post("/api/v1/invite/accept", json={"invitation_link": invitation_link})
        assert response.status_code == 200
        assert response.json()["message"] == "User added to organization successfully"

@pytest.mark.asyncio
async def test_expired_invitation(test_app, create_invitation, create_user_and_org):
    user_id, org_id = create_user_and_org
    invitation = create_invitation(user_id=user_id, organization_id=org_id, expires_at=datetime.utcnow() - timedelta(days=1))

    invitation_link = f"http://test/api/v1/invite/accept?invitation_id={invitation.id}"

    async with AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.post("/api/v1/invite/accept", json={"invitation_link": invitation_link})
        assert response.status_code == 400
        assert response.json()["detail"] == "Expired invitation link"

@pytest.mark.asyncio
async def test_malformed_invitation(test_app):
    invitation_link = "http://test/api/v1/invite/accept?invitation_id=malformed"

    async with AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.post("/api/v1/invite/accept", json={"invitation_link": invitation_link})
        assert response.status_code == 400  # Should be 400 for malformed ID
        assert response.json()["detail"] == "Invalid invitation link"

@pytest.mark.asyncio
async def test_load_invitation(test_app, create_invitation, create_user_and_org):
    user_id, org_id = create_user_and_org
    invitation = create_invitation(user_id=user_id, organization_id=org_id)

    invitation_link = f"http://test/api/v1/invite/accept?invitation_id={invitation.id}"

    async with AsyncClient(app=test_app, base_url="http://test") as client:
        tasks = []
        for _ in range(100):  # Adjust the number for load testing
            tasks.append(client.post("/api/v1/invite/accept", json={"invitation_link": invitation_link}))
        responses = await asyncio.gather(*tasks)
        for response in responses:
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main()
