"""
Tests for delete product endpoint
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
from api.v1.models.product import Product
from api.v1.services.user import user_service, UserService


client = TestClient(app)


def endpoint(org_id, product_id):
    return f"/api/v1/organisations/{org_id}/products/{product_id}"


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
        "api.v1.services.product.ProductService.delete", autospec=True
    ) as mock_delete:
        yield mock_delete


@pytest.fixture
def override_get_current_user():
    """Mock the get_current_user dependency"""

    app.dependency_overrides[user_service.get_current_user] = lambda: User(
        id=str(uuid7()),
        email="admintestuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="AdminTest",
        last_name="User",
        is_active=True,
        # organisations=[org_1],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


mock_id = str(uuid7())
mock_org_id = str(uuid7())


def create_dummy_mock_product(mock_user_service: UserService, mock_db_session: Session):
    """generate a dummy mock product

    Args:
        mock_user_service (UserService): mock user service
        mock_db_session (Session): mock database session
    """
    dummy_mock_product = Product(
        id=mock_id,
        name="Product 1",
        description="Description for product 1",
        price=19.99,
        org_id=mock_org_id,
        category_id=str(uuid7()),
        image_url="random.com",
    )
    mock_db_session.get.return_value = dummy_mock_product
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None


@pytest.mark.usefixtures("mock_db_session", "mock_user_service")
def test_unauthorised_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.delete(endpoint(mock_org_id, mock_id))

    print(response.json())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures(
    "mock_db_session",
    "mock_user_service",
    "override_get_current_user",
    "override_delete",
)
def test_successful_deletion(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_user: None,
    override_delete: None,
):
    """Test for successful deletion of product"""

    # Create a mock user
    create_dummy_mock_product(mock_user_service, mock_db_session)
    mock_db_session.get.return_value = mock_db_session.get.return_value

    response = client.delete(
        endpoint(mock_org_id, mock_id),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.usefixtures(
    "mock_db_session",
    "mock_user_service",
    "override_get_current_user",
)
def test_already_deleted(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_user: None,
):
    """Test deletion of already deleted product"""

    # Simulate the user being deleted from the database
    mock_db_session.get.return_value = None

    response = client.delete(
        endpoint(mock_org_id, mock_id),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures(
    "mock_db_session", "mock_user_service", "override_get_current_user"
)
def test_not_found_error(
    mock_user_service: UserService,
    mock_db_session: Session,
    override_get_current_user: None,
):
    """Test for invalid product ID"""

    # Simulate the product not being found in the database
    mock_db_session.get.return_value = None

    response = client.delete(
        endpoint(mock_org_id, mock_id),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
