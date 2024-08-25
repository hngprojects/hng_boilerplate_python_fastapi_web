from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid_extensions import uuid7
import pytest

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.email_template import EmailTemplate
from api.v1.services.email_template import email_template_service
from main import app


# Mocked data and services
def mock_get_current_admin():
    return User(
        id=str(uuid7()),
        email="admin@gmail.com",
        password=user_service.hash_password("Testadmin@123"),
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


def mock_email_template():
    return EmailTemplate(
        id=str(uuid7()),
        title="Test title",
        type="Test type",
        template="<h1>Hello</h1>",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def db_session_mock():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def client(db_session_mock):
    app.dependency_overrides[get_db] = lambda: db_session_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_send_email_template_success(client, db_session_mock):
    """Test successfully sending an email template"""

    # Mock the current admin user and email template
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin()
    app.dependency_overrides[email_template_service.fetch] = lambda db, template_id: mock_email_template()

    with patch("api.v1.services.email_template.email_template_service.send") as mock_send:
        mock_send.return_value = {"status": "success", "message": "Email sent to recipient@example.com"}

        # recipient_email is passed as a query parameter now
        response = client.post(
            f'/api/v1/email-templates/{mock_email_template().id}/send?recipient_email=recipient@example.com',
            headers={'Authorization': 'Bearer token'},
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Email sent successfully to recipient@example.com"


def test_send_email_template_failure(client, db_session_mock):
    """Test failing to send an email template with retry mechanism"""

    # Mock the current admin user and email template
    app.dependency_overrides[user_service.get_current_super_admin] = lambda: mock_get_current_admin()
    app.dependency_overrides[email_template_service.fetch] = lambda db, template_id: mock_email_template()

    with patch("api.v1.services.email_template.email_template_service.send") as mock_send:
        mock_send.return_value = {"status": "failure", "message": "Failed to send email after multiple attempts"}

        response = client.post(
            f'/api/v1/email-templates/{mock_email_template().id}/send?recipient_email=recipient@example.com',
            headers={'Authorization': 'Bearer token'},
        )

        assert response.status_code == 500
        assert response.json()["message"] == "Failed to send email after multiple attempts"




def test_send_email_template_unauthorized(client, db_session_mock):
    """Test sending email template by unauthorized user"""

    response = client.post(
        f'/api/v1/email-templates/{mock_email_template().id}/send',
        json={"recipient_email": "recipient@example.com"},
    )

    assert response.status_code == 401
