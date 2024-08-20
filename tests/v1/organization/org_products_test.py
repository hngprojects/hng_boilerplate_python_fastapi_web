import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models import User, Product, Organisation
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from unittest.mock import MagicMock

client = TestClient(app)


# Mock database
@pytest.fixture
def mock_db_session(mocker):
    db_session_mock = mocker.MagicMock(spec=Session)
    app.dependency_overrides[get_db] = lambda: db_session_mock
    return db_session_mock


# Test User
@pytest.fixture
def test_user():
    return User(
        id=str(uuid7()),
        email="testuser@gmail.com",
        password="hashedpassword",
        first_name="test",
        last_name="user",
        is_active=True,
    )


# Another Test User
@pytest.fixture
def another_user():
    return User(
        id=str(uuid7()),
        email="anotheruser@gmail.com",
        password="hashedpassword",
        first_name="another",
        last_name="user",
        is_active=True,
    )


@pytest.fixture
def test_organisation(test_user):
    organisation = Organisation(
        id=str(uuid7()),
        name="testorg",
    )
    organisation.users.append(test_user)
    return organisation


@pytest.fixture()
def test_product(test_organisation):
    return Product(
        id=str(uuid7()),
        name="testproduct",
        description="Test product",
        price=9.99,
        org_id=test_organisation.id,
    )


@pytest.fixture
def access_token_user1(test_user):
    return user_service.create_access_token(user_id=test_user.id)


@pytest.fixture
def access_token_user2(another_user):
    return user_service.create_access_token(user_id=another_user.id)


# Test for User in Organisation
def test_get_products_for_organisation_user_belongs(
    mock_db_session,
    test_user,
    test_organisation,
    test_product,
    access_token_user1,
):
    # Mock the GET method for Organisation
    def mock_get(model, ident):
        if model == Organisation and ident == test_organisation.id:
            return test_organisation
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query for checking if user is in the organisation
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        test_user
    )

    # Mock the query for products
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        test_product
    ]

    # Test user belonging to the organisation
    headers = {"Authorization": f"Bearer {access_token_user1}"}
    response = client.get(
        f"/api/v1/organisations/{test_organisation.id}/products", headers=headers
    )

    # Debugging statement
    if response.status_code != 200:
        print(response.json())  # Print error message for more details

    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"
    # products = response.json().get('data', [])


### Test for user not in Organisation
def test_get_products_for_organisation_user_not_belong(
    mock_db_session,
    another_user,
    test_organisation,
    test_product,
    access_token_user2,
):
    # Ensure the organisation does not contain another_user
    test_organisation.users = []

    # Mock the `get` method for `Organisation`
    def mock_get(model, ident):
        if model == Organisation and ident == test_organisation.id:
            return test_organisation
        return None

    mock_db_session.get.side_effect = mock_get

    # Mock the query for checking if user is in the organisation
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        another_user
    )

    # Test user not belonging to the organisation
    headers = {"Authorization": f"Bearer {access_token_user2}"}
    response = client.get(
        f"/api/v1/organisations/{test_organisation.id}/products", headers=headers
    )

    assert (
        response.status_code == 400
    ), f"Expected status code 400, got {response.status_code}"


### Test for non-existent Organisation
def test_get_products_for_non_existent_organisation(
    mock_db_session,
    test_user,
    access_token_user1,
):
    # Mock the `get` method for `Organisation` to return None for non-existent ID
    def mock_get(model, ident):
        return None

    mock_db_session.get.side_effect = mock_get

    # Test non-existent organisation
    non_existent_id = "non-existent-id"  # Use a string since the IDs are UUIDs
    headers = {"Authorization": f"Bearer {access_token_user1}"}
    response = client.get(
        f"/api/v1/organisations/{non_existent_id}/products", headers=headers
    )

    assert (
        response.status_code == 404
    ), f"Expected status code 404, got {response.status_code}"
