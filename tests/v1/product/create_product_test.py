"""
Tests for create product endpoint
"""

from typing import Any
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from main import app
from uuid_extensions import uuid7
from fastapi import status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.product import Product
from api.v1.models.organisation import Organisation
from api.v1.services.user import user_service, UserService
from api.v1.services.product import product_service, ProductService
from api.utils.db_validators import check_user_in_org


client = TestClient(app)
PRODUCT_ENDPOINT = "/api/v1/organisations"


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
def override_create():
    """Mock the create method"""

    with patch(
        "api.v1.services.product.ProductService.create", autospec=True
    ) as mock_create:
        mock_create.return_value = Product(
            id=str(uuid7()),
            name="Product 1",
            description="Description for product 1",
            price=19.99,
            org_id=str(uuid7()),
            category_id=str(uuid7()),
            image_url="random.com",
        )

        yield mock_create


@pytest.fixture
def mock_invalid_category():
    with patch(
        "api.v1.services.product.ProductService.create", autospec=True
    ) as mock_create:
        mock_create.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        yield mock_create


@pytest.fixture
def mock_foriegn_org():
    with patch(
        "api.v1.services.product.ProductService.create", autospec=True
    ) as mock_create:
        mock_create.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this organisation",
        )

        yield mock_create


@pytest.fixture
def mock_get_current_user():
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

SAMPLE_DATA = {"name": "delete me", "price": 99.99, "category": "STufF"}


def test_successful_creation(
    mock_user_service: UserService,
    mock_db_session: Session,
    mock_get_current_user: None,
    override_create: None,
):
    """Test for succesful creation of product"""

    response = client.post(
        f"{PRODUCT_ENDPOINT}/{mock_id}/products",
        json=SAMPLE_DATA,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Product created successfully"


def test_unauthorized_access(mock_user_service: UserService, mock_db_session: Session):
    """Test for unauthorized access to endpoint."""

    response = client.post(
        f"{PRODUCT_ENDPOINT}/{str(uuid7())}/products", json=SAMPLE_DATA
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_non_existent_organisation(
    mock_user_service: UserService,
    mock_db_session: Session,
    mock_get_current_user: None,
):
    """Test for invalid org ID"""

    # Simulate the organisation not being found in the database
    mock_db_session.get.return_value = None

    response = client.post(
        f"{PRODUCT_ENDPOINT}/{str(uuid7())}/products", json=SAMPLE_DATA
    )

    print(response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_non_existent_category(
    mock_user_service: UserService,
    mock_db_session: Session,
    mock_get_current_user: None,
    mock_invalid_category: MagicMock | AsyncMock,
):
    """Test for invalid category"""

    response = client.post(
        f"{PRODUCT_ENDPOINT}/{str(uuid7())}/products", json=SAMPLE_DATA
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_does_not_belong_to_org(
    mock_user_service: UserService,
    mock_db_session: Session,
    mock_get_current_user: None,
    mock_foriegn_org: MagicMock | AsyncMock,
):
    """Test if user belongs to organisation with the org ID"""

    response = client.post(
        f"{PRODUCT_ENDPOINT}/{str(uuid7())}/products", json=SAMPLE_DATA
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["message"] == "You are not a member of this organisation"
