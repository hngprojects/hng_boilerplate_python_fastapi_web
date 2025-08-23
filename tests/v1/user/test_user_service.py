import pytest
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.services.user import UserService
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def user_service():
    return UserService()

def test_fetch_all_search(db_session, user_service):
    # Mock users with all required fields
    created_at = datetime.now()
    updated_at = datetime.now()
    user1 = User(
        id="1",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        is_active=True,
        is_deleted=False,
        is_verified=True,
        is_superadmin=False,
        created_at=created_at,
        updated_at=updated_at
    )
    db_session.query().filter().order_by().limit().offset().all.return_value = [user1]
    db_session.query().filter().count.return_value = 1

    response = user_service.fetch_all(db_session, page=1, limit=20, search="john")
    assert response.status_code == 200
    assert len(response.data["users"]) == 1
    assert response.data["users"][0].first_name == "John"
    assert response.data["pagination"].total_users == 1  # Access as attribute
    assert response.data["pagination"].total_pages == 1  # Access as attribute

def test_fetch_all_is_active_filter(db_session, user_service):
    created_at = datetime.now()
    updated_at = datetime.now()
    user1 = User(
        id="1",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        is_active=True,
        is_deleted=False,
        is_verified=True,
        is_superadmin=False,
        created_at=created_at,
        updated_at=updated_at
    )
    db_session.query().filter().order_by().limit().offset().all.return_value = [user1]
    db_session.query().filter().count.return_value = 1

    response = user_service.fetch_all(db_session, page=1, limit=20, is_active=True)
    assert response.status_code == 200
    assert len(response.data["users"]) == 1
    assert response.data["users"][0].is_active is True

def test_fetch_all_pagination(db_session, user_service):
    created_at = datetime.now()
    updated_at = datetime.now()
    users = [
        User(
            id=str(i),
            first_name=f"User{i}",
            last_name="Test",
            email=f"user{i}@example.com",
            is_active=True,
            is_deleted=False,
            is_verified=True,
            is_superadmin=False,
            created_at=created_at,
            updated_at=updated_at
        ) for i in range(25)
    ]
    db_session.query().order_by().limit().offset().all.return_value = users[:20]
    db_session.query().count.return_value = 25

    response = user_service.fetch_all(db_session, page=1, limit=20)
    assert response.data["pagination"].page == 1
    assert response.data["pagination"].limit == 20
    assert response.data["pagination"].total_users == 25
    assert response.data["pagination"].total_pages == 2
    assert len(response.data["users"]) == 20