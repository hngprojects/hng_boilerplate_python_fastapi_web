import pytest
from api.v1.models.user import User
from uuid_extensions import uuid7
from api.v1.services.user import user_service
from datetime import datetime, timezone
from main import app
from api.v1.models.totp_device import TOTPDevice
from api.v1.services.totp import totp_service
from fastapi.testclient import TestClient
from fastapi import status, HTTPException


class TestTOTPDevice:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_user = User(
            id=str(uuid7()),
            email="testuser@gmail.com",
            password=user_service.hash_password("Testpassword@123"),
            first_name="Test",
            last_name="User",
            is_active=True,
            is_superadmin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        app.dependency_overrides[user_service.get_current_user] = lambda: self.test_user
        self.client = TestClient(app)
        self.test_secret = "TESTSECRET"
        self.test_otpauth_url = "otpauth://test?secret=TESTSECRET&issuer=app"
        self.test_qrcode_base64 = "BASE64STRING"
        self.test_token = "123456"
        self.test_totp_device_data_enable_success = {"user_id": self.test_user.id, "confirmed": True}
        self.test_totp_device_data_disable_success = {"user_id": self.test_user.id, "confirmed": False}
        yield
        app.dependency_overrides.pop(user_service.get_current_user)

    def test_setup_2fa_success(self, monkeypatch):
        """Test for successful TOTP device creation"""

        mock_totp_device = TOTPDevice(
            id=str(uuid7()),
            user_id=self.test_user.id,
            secret=self.test_secret,
            confirmed=False,
        )
        monkeypatch.setattr(totp_service, "create", lambda db, schema: mock_totp_device)
        monkeypatch.setattr(totp_service, "generate_secret", lambda: self.test_secret)
        monkeypatch.setattr(
            totp_service,
            "generate_otpauth_url",
            lambda secret, user_email, app_name: self.test_otpauth_url,
        )
        monkeypatch.setattr(
            totp_service, "generate_qrcode", lambda otpauth_url: self.test_qrcode_base64
        )

        response = self.client.post("api/v1/auth/setup-2fa")
        response_json = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert response_json.get("message") == "TOTP device created successfully."

        data = response_json.get("data")
        assert data is not None
        assert data.get("secret") == self.test_secret
        assert data.get("otpauth_url") == self.test_otpauth_url
        assert data.get("qrcode_base64") == self.test_qrcode_base64

    def test_setup_2fa_failure_existing_device(self, monkeypatch):
        """Test that setting up 2FA fails when device already exists"""

        mock_totp_device = TOTPDevice(
            id=str(uuid7()),
            user_id=self.test_user.id,
            secret=self.test_secret,
            confirmed=False,
        )
        monkeypatch.setattr(totp_service, "fetch", lambda db, user_id: mock_totp_device)
        monkeypatch.setattr(totp_service, "generate_secret", lambda: self.test_secret)

        response = self.client.post("api/v1/auth/setup-2fa")
        response_json = response.json()

        assert response.status_code == status.HTTP_409_CONFLICT
        assert (
            response_json.get("message") == "totp device for this user already exists"
        )

    def test_setup_2fa_failure_unauthenticated(self, monkeypatch):
        """Test that setting up 2FA fails when user is not authenticated"""

        app.dependency_overrides.pop(user_service.get_current_user, None)

        def mock_auth_error():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        app.dependency_overrides[user_service.get_current_user] = mock_auth_error

        response = self.client.post("api/v1/auth/setup-2fa")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        app.dependency_overrides[user_service.get_current_user] = lambda: self.test_user

    def test_enable_2fa_success(self, monkeypatch):
        """Test that enabling TOTP device returns a 202 response with the expected data"""

        mock_totp_device = TOTPDevice(
            id=str(uuid7()),
            user_id=self.test_user.id,
            secret=self.test_secret,
            confirmed=False,
        )
        
        def mock_verify_token(db, user_id, schema, extra_action=None):
            if extra_action == "enable":
                mock_totp_device.confirmed = True
                return mock_totp_device
            return None
        
        monkeypatch.setattr(
            totp_service,
            "verify_token",
            mock_verify_token
        )
    
        payload = {"totp_token": self.test_token}
        
        response = self.client.put("api/v1/auth/enable-2fa", json=payload)
        response_json = response.json()
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response_json.get("message") == "TOTP device enabled successfully."
        assert response_json.get("data") == self.test_totp_device_data_enable_success
        
    def test_disable_2fa_success(self, monkeypatch):
        """Test that disabling TOTP device returns a 202 response with the expected data"""

        mock_totp_device = TOTPDevice(
            id=str(uuid7()),
            user_id=self.test_user.id,
            secret=self.test_secret,
            confirmed=False,
        )
        
        def mock_verify_token(db, user_id, schema, extra_action=None):
            if extra_action == "disable":
                mock_totp_device.confirmed = False
                return mock_totp_device
            return None
        
        monkeypatch.setattr(
            totp_service,
            "verify_token",
            mock_verify_token
        )
    
        payload = {"totp_token": self.test_token}
        
        response = self.client.put("api/v1/auth/disable-2fa", json=payload)
        response_json = response.json()
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response_json.get("message") == "TOTP device disabled successfully."
        assert response_json.get("data") == self.test_totp_device_data_disable_success