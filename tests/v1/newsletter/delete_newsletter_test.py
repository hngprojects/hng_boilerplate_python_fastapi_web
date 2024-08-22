"""
Test for delete newsletter endpoint
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from uuid_extensions import uuid7
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.newsletter import Newsletter
from api.v1.services.user import user_service, UserService
from api.v1.services.newsletter import NewsletterService

client = TestClient(app)
ENDPOINT = "/api/v1/newsletters"


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."

    Yields:
        MagicMock: mock database
    """

    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""

    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service


@pytest.fixture
def override_delete():
    """Mock the delete method"""

    # app.dependency_overrides[product_service.delete] = lambda: None

    with patch(
        "api.v1.services.newsletter.NewsletterService.delete", autospec=True
    ) as mock_delete:
        yield mock_delete

@pytest.fixture
def override_get_current_super_admin():
    """Mock the get_current_super_admin dependency"""

    app.dependency_overrides[user_service.get_current_super_admin] = lambda: User(
        id=str(uuid7()),
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=False,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

mock_id = str(uuid7())

def test_unauthorised_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.delete(f"{ENDPOINT}/{mock_id}")

    print(response.json())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_successful_deletion(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_delete: None,
    override_get_current_super_admin: None
):
    """Test for successful deletion of newsletter"""

    response = client.delete(f"{ENDPOINT}/{mock_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_not_found_error(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_super_admin: None,
):
    """Test for invalid newsletter ID"""

    # Simulate the product not being found in the database
    mock_db_session.get.return_value = None

    response = client.delete(f"{ENDPOINT}/{mock_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
