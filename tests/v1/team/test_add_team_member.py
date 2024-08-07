# Dependencies:
# pip install pytest-mock
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.db.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from api.v1.schemas.team import PostTeamMemberSchema
from api.v1.services.user import oauth2_scheme


def mock_deps():
    return MagicMock(id="user_id")


def mock_db():
    return MagicMock(spec=Session)


def mock_oauth():
    return 'access_token'


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


class TestCodeUnderTest:
    @classmethod
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
        app.dependency_overrides[get_db] = mock_db

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully adding a member to the database

    def test_add_members_success(self, client):
        test_member = {"name": "Mark",
                       "description": "A graphic artist",
                       "role": "admin",
                       "picture_url": "example.com",
                       "team_type": "Executive"}

        with patch('api.v1.services.team.TeamServices.create') as mock_team:
            mock_team.return_value = MagicMock(spec=PostTeamMemberSchema,
                                               id='user_id',
                                               created_at=datetime.now())

            with patch('api.v1.schemas.team.TeamMemberCreateResponseSchema.model_validate') as sc:
                sc.return_value = test_member
                response = client.post(
                    "/api/v1/team/members", json=test_member)

                assert response.status_code == 201
                assert response.json()[
                    'message'] == "Team Member added successfully"

                assert response.json()['data']['name'] == test_member['name']
                assert response.json()['success'] == True

    # Handling empty description field and raising appropriate exception
    def test_add_members_empty_desc(self, client):
        test_member = {"name": "Mark",
                       "description": "",
                       "role": "admin",
                       "picture_url": "example.com",
                       "team_type": "Executive"}

        response = client.post("/api/v1/team/members", json=test_member)
        assert response.status_code == 422
        assert response.json()['message'] == 'Invalid input'

    # Handling absent role field and raising appropriate exception
    def test_add_members_absent_role(self, client):
        test_member = {"name": "Mark",
                       "description": "A graphic artist",
                       "picture_url": "example.com",
                       "team_type": "Executive"}

        response = client.post("/api/v1/team/members", json=test_member)
        assert response.status_code == 422

    # Handling unauthorized request
    def test_add_members_unauthorized(self, client):

        test_member = {"name": "Mark",
                       "description": "A graphic artist",
                       "role": "admin",
                       "picture_url": "example.com",
                       "team_type": "Executive"}

        app.dependency_overrides = {}

        response = client.post("/api/v1/team/members", json=test_member)
        assert response.status_code == 401
        assert response.json()['message'] == 'Not authenticated'

  # Handling forbidden request
    def test_add_members_forbidden(self, client):

        test_member = {"name": "Mark",
                       "description": "A graphic artist",
                       "role": "admin",
                       "picture_url": "example.com",
                       "team_type": "Executive"}

        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = mock_db
        app.dependency_overrides[oauth2_scheme] = mock_oauth

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_super_admin=False)) as cu:
            response = client.post("/api/v1/team/members", json=test_member)
        assert response.status_code == 403
        assert response.json()[
            'message'] == 'You do not have permission to access this resource'
