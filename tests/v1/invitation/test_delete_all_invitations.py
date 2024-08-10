# Dependencies:
# pip install pytest-mock
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.v1.services.user import oauth2_scheme

from api.v1.services.invite import InviteService
from sqlalchemy.orm import Session


db_mck = MagicMock(spec=Session)
def mock_deps():
    return MagicMock(id="user_id")

def mock_oauth():
    return 'access_token'

def mock_db():
    return db_mck

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

DELETE_ENDPOINT = "/api/v1/invite"
class TestDeleteAllInvite:
    @classmethod
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
        app.dependency_overrides[get_db] = mock_db

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}


    # Successfully delete all invitations when called by a super admin
    def test_delete_all_invite_success(self, mocker, client):
        
        mocker.patch.object(InviteService, 'delete_all')
        response = client.delete(DELETE_ENDPOINT)

        InviteService.delete_all.assert_called_once_with(db_mck)
        assert response.status_code == 204

        # Handling unauthorized request
    def test_delete_all_invite_unauth(self, client):
        app.dependency_overrides = {}

        response = client.delete(DELETE_ENDPOINT)
        assert response.status_code == 401
        assert response.json()['message'] == 'Not authenticated'

  # Handling forbidden request
    def test_delete_all_invite_forbidden(self, client):
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = mock_db
        app.dependency_overrides[oauth2_scheme] = mock_oauth

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_superadmin=False)) as cu:
            response = client.delete(DELETE_ENDPOINT)
            assert response.status_code == 403
            assert response.json()['message'] == 'You do not have permission to access this resource'
