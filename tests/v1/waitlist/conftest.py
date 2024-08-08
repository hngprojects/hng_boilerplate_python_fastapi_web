from fastapi import HTTPException
import pytest
from unittest.mock import patch, MagicMock
from api.db.database import get_db
from main import app
from api.utils.dependencies import get_super_admin


def mock_super_admin():
    return MagicMock(is_admin=True)


@pytest.fixture
def mock_db_session():
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


@pytest.fixture
def mock_user_service():
    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service


@pytest.fixture
def mock_delete_waitlist_success():
    with patch("api.v1.services.waitlist.waitlist_service.delete") as delete_waitlist:
        yield delete_waitlist


@pytest.fixture
def mock_admin_user():
    with patch("api.utils.dependencies.get_super_admin"):
        app.dependency_overrides[get_super_admin] = mock_super_admin


@pytest.fixture
def mock_waitlist_not_found():
    with patch("api.v1.services.waitlist.waitlist_service.delete") as delete_waitlist:
        delete_waitlist.side_effect = HTTPException(
            404, "No waitlisted user found with given id"
        )

        yield delete_waitlist
