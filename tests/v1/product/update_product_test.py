from datetime import datetime, timedelta
from unittest.mock import MagicMock
from fastapi import HTTPException
from jose import JWTError, jwt
import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.models.user import User
from api.db.database import get_db

client = TestClient(app)


@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session


@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_jwt_decode(mocker):
    return mocker.patch("jose.jwt.decode", return_value={"user_id": "user_id"})


@pytest.fixture
def mock_get_current_user(mocker):
    user = User(id="user_id", is_super_admin=False)
    mock = mocker.patch("api.utils.dependencies.get_current_user", return_value=user)
    return mock


def create_test_token(user_id: str) -> str:
    expires = datetime.utcnow() + timedelta(minutes=30)
    data = {"user_id": user_id, "exp": expires}
    return jwt.encode(data, "secret", algorithm="HS256")


def test_update_product_with_valid_token(
    db_session_mock, mock_get_current_user, mock_jwt_decode, mocker
):
    """Test product update with a valid token."""
    mocker.patch("jose.jwt.decode", return_value={"user_id": "user_id"})

    mock_product = MagicMock()
    mock_product.id = "c9752bcc-1cf4-4476-a1ee-84b19fd0c521"
    mock_product.name = "Old Product"
    mock_product.price = 20.0
    mock_product.description = "Old Description"
    mock_product.updated_at = None
    db_session_mock().query().filter().first.return_value = mock_product

    def mock_commit():
        mock_product.name = "Updated Product"
        mock_product.price = 25.0
        mock_product.description = "Updated Description"
        mock_product.updated_at = datetime.utcnow()

    db_session_mock().commit = mock_commit

    product_update = {
        "name": "Updated Product",
        "price": 25.0,
        "description": "Updated Description",
    }

    token = create_test_token("user_id")

    response = client.put(
        "/api/v1/products/c9752bcc-1cf4-4476-a1ee-84b19fd0c521",
        json=product_update,
        headers={"Authorization": f"Bearer {token}"},
    )

    print("Update response:", response.json())  # Debugging output

    assert response.status_code == 200
    
    
def test_update_product_with_invalid_token(db_session_mock, mock_get_current_user, mocker):
    """Test product update with an invalid token."""
    mocker.patch("jose.jwt.decode", side_effect=JWTError("Invalid token"))

    mocker.patch(
        "api.utils.dependencies.get_current_user",
        side_effect=HTTPException(status_code=401, detail="Invalid credentials"),
    )

    response = client.put(
        "/api/v1/products/c9752bcc-1cf4-4476-a1ee-84b19fd0c521",
        json={"name": "Product"},
        headers={"Authorization": "Bearer invalid_token"},
    )

    print("Invalid token response:", response.json())  # Debugging output
    assert response.status_code == 401
    assert (
        response.json()["message"] == "Could not validate crenentials"
    )  # Adjusted assertion


def test_update_product_with_missing_fields(
    db_session_mock, mock_get_current_user, mock_jwt_decode, mocker
):
    """Test product update with missing fields."""
    mocker.patch("jose.jwt.decode", return_value={"user_id": "user_id"})

    token = create_test_token("user_id")

    response = client.put(
        "/api/v1/products/c9752bcc-1cf4-4476-a1ee-84b19fd0c521",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Missing fields response: {response.json()}")  # Debugging output
    assert response.status_code == 422

    errors = response.json().get("errors", [])
    assert isinstance(errors, list)
    assert any("Field required" in error.get("msg", "") for error in errors)


def test_update_product_with_special_characters(
    db_session_mock, mock_get_current_user, mock_jwt_decode, mocker
):
    """Test product update with special characters in the product name."""
    mocker.patch("jose.jwt.decode", return_value={"user_id": "user_id"})

    mock_product = MagicMock()
    mock_product.id = "c9752bcc-1cf4-4476-a1ee-84b19fd0c521"
    mock_product.name = "Special Prod@uct"
    mock_product.price = 100.0
    mock_product.description = "Special Description"
    mock_product.updated_at = None

    db_session_mock().query().filter().first.return_value = mock_product

    def mock_commit():
        mock_product.name = "Updated @Product! #2024"
        mock_product.price = 99.99
        mock_product.description = "Updated & Description!"
        mock_product.updated_at = datetime.utcnow()

    db_session_mock().commit = mock_commit

    product_update = {
        "name": "Updated @Product! #2024",
        "price": 99.99,
        "description": "Updated & Description!",
    }

    token = create_test_token("user_id")

    response = client.put(
        "/api/v1/products/c9752bcc-1cf4-4476-a1ee-84b19fd0c521",
        json=product_update,
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Special characters response: {response.json()}")  # Debugging output
    assert response.status_code == 200
