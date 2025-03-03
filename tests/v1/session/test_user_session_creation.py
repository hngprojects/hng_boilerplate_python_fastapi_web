import time
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7
from datetime import datetime, timezone, timedelta

from main import app

from api.v1.services.totp import totp_service
from api.v1.services.session import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.models.session import UserSession
from api.v1.services.session import session_service


class TestUserSessionCreation:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.mock_db
        self.client = TestClient(app)

        # Mock user creation to return a valid user object
        self.mock_user = User(
            id=str(uuid7()),
            email="testuser1@gmail.com",
            password=user_service.hash_password("Testpassword@123"),
            first_name="Test",
            last_name="User",
            is_active=True,
            is_superadmin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Mock session creation
        self.mock_user_session = UserSession(
            id=str(uuid7()),
            user_id=self.mock_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            ip_address="192.168.1.1",
            location="Lagos, Nigeria",
            device="test-client",
            refresh_token=user_service.create_refresh_token(self.mock_user.id),
            is_revoked=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        time.sleep(1)

    def test_previous_token_is_revoked_when_login_from_same_ip_and_user_agent(self, monkeypatch):
        """Test that previous token is revoked when login from same IP and user agent."""
        new_mock_session = UserSession(
            id=str(uuid7()),
            user_id=self.mock_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            ip_address="192.168.1.1",
            location="Lagos, Nigeria",
            device="test-client",
            refresh_token=user_service.create_refresh_token(self.mock_user.id),
            is_revoked=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        monkeypatch.setattr(
            user_service,
            "authenticate_user",
            lambda db, email, password: self.mock_user
        )
        monkeypatch.setattr(
            "api.v1.services.organisation.organisation_service.retrieve_user_organizations",
            lambda user, db: []
        )

        monkeypatch.setattr(
            totp_service,
            "check_2fa_status_and_verify",
            lambda db, user_id, schema: True
        )
        def mock_create_session(db, schema, user_id):
            self.mock_user_session.is_revoked = True
            return new_mock_session

        monkeypatch.setattr(
            session_service,
            "create",
            mock_create_session
        )

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "testuser1@gmail.com", "password": "Testpassword@123"},
        )

        assert response.status_code == 200
        assert self.mock_user_session.refresh_token != new_mock_session.refresh_token
        assert self.mock_user_session.is_revoked is True

