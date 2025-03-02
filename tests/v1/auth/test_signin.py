import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.totp import totp_service
from uuid_extensions import uuid7
from api.db.database import get_db
from fastapi import status
from datetime import datetime, timezone
from api.v1.models.totp_device import TOTPDevice
import pyotp

# Client for test_user_login function
client = TestClient(app)


class TestUserLogin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)
        self.mock_user = User(
            id=str(uuid7()),
            email="testuser1@gmail.com",
            password=user_service.hash_password("Testpassword@123"),
            first_name="Test",
            last_name="User",
            is_active=True,
            is_superadmin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.mock_totp_device = TOTPDevice(
            user_id=self.mock_user.id,
            secret=pyotp.random_base32(),
            confirmed=False,
        )
        self.mock_totp_code = pyotp.TOTP(self.mock_totp_device.secret).now()

    def test_user_login_success_without_2FA(self, monkeypatch):
        """Test successful login without 2FA"""

        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )
        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: True
        )
        monkeypatch.setattr(
            "api.v1.services.organisation.organisation_service.retrieve_user_organizations",
            lambda user, db: []
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "testuser1@gmail.com", "password": "Testpassword@123"},
        )
        response_json = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_json.get("status_code") == status.HTTP_200_OK
        assert response_json.get("message") == "Login successful"

    def test_user_login_success_with_2FA(self, monkeypatch):
        """Test successful login with 2FA enabled and valid code"""

        self.mock_totp_device.confirmed = True
        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )
        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: True
        )
        monkeypatch.setattr(
            "api.v1.services.organisation.organisation_service.retrieve_user_organizations",
            lambda user, db: []
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser1@gmail.com",
                "password": "Testpassword@123",
                "totp_code": f"{self.mock_totp_code}"
            },
        )
        response_json = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_json.get("status_code") == status.HTTP_200_OK
        assert response_json.get("message") == "Login successful"

    def test_user_login_success_with_2FA_disabled(self, monkeypatch):
        """Test successful login with 2FA set up but not confirmed/enabled"""

        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )
        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: True
        )
        monkeypatch.setattr(
            "api.v1.services.organisation.organisation_service.retrieve_user_organizations",
            lambda user, db: []
        )
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "testuser1@gmail.com", "password": "Testpassword@123"},
        )

        response_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_json.get("status_code") == status.HTTP_200_OK
        assert response_json.get("message") == "Login successful"

    def test_user_login_failure_with_2FA_enabled_without_code(self, monkeypatch):
        """Test login failure when 2FA is enabled but no code is provided"""

        self.mock_totp_device.confirmed = True
        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )

        def mock_check_2fa_status_and_verify():
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is enabled for this user. Provide a valid TOTP code."
            )

        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: mock_check_2fa_status_and_verify()
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "testuser1@gmail.com", "password": "Testpassword@123"},
        )
        response_json = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json.get("status_code") == status.HTTP_400_BAD_REQUEST
        assert response_json.get("message") == "2FA is enabled for this user. Provide a valid TOTP code."

    def test_user_login_failure_with_2FA_enabled_with_invalid_code(self, monkeypatch):
        """Test login failure when 2FA is enabled but the code is invalid"""

        self.mock_totp_device.confirmed = True
        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )

        def mock_verify_invalid_code():
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )

        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: mock_verify_invalid_code()
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser1@gmail.com",
                "password": "Testpassword@123",
                "totp_code": "123456"
            },
        )
        response_json = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json.get("status_code") == status.HTTP_400_BAD_REQUEST
        assert response_json.get("message") == "Invalid TOTP code"

    def test_inactive_user_login(self, monkeypatch):
        """Test for inactive user login attempt"""

        self.mock_user.is_active = False
        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )
        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: True
        )
        monkeypatch.setattr(
            "api.v1.services.organisation.organisation_service.retrieve_user_organizations",
            lambda user, db: []
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "testuser1@gmail.com", "password": "Testpassword@123"},
        )
        response_json = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_json.get("status_code") == status.HTTP_200_OK
        assert response_json.get("message") == "Login successful"
        assert not response_json.get("data").get("user").get("is_active")

    def test_swagger_ui_auth_form_handling(self):
        """Test that the Swagger UI authentication form handling works correctly."""

        # This test simulates how Swagger UI sends authentication data
        # It uses form data instead of JSON
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": "testuser1@gmail.com", "password": "Testpassword@123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        # We expect a 422 error (not 500) with clear validation message
        assert response.status_code == 422
        response_json = response.json()
        assert "detail" in response_json or "errors" in response_json
        assert response_json.get("status_code") == 422
        assert response_json.get("message") == "Invalid input" or "Invalid" in response_json.get("message", "")


# Mock the database dependency
@pytest.fixture
def db_session_mock():
    db_session = MagicMock()
    yield db_session


# Override the dependency with the mock
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = get_db_override
    yield
    # Clean up after the test by removing the override
    app.dependency_overrides = {}


def test_user_login(db_session_mock):
    """Test for successful inactive user login."""

    # Create a mock user
    mock_user = User(
        id=str(uuid7()),
        email="testuser1@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name='Test',
        last_name='User',
        is_active=False,
        is_superadmin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_user

    # Login with mock user details
    login = client.post("/api/v1/auth/login", json={
        "email": "testuser1@gmail.com",
        "password": "Testpassword@123"
    })
    response = login.json()
    assert response.get("status_code") == status.HTTP_200_OK