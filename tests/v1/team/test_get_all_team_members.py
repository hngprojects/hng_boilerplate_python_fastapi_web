import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from api.v1.services.user import user_service
from api.db.database import get_db
from sqlalchemy.orm import Session
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


class TestGetAllTeamMembers:
    @classmethod
    def setup_class(cls):
        app.dependency_overrides[user_service.get_current_super_admin] = mock_deps
        app.dependency_overrides[get_db] = mock_db

    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully retrieving all team members
    def test_get_all_team_members_success(self, client):
        test_members = [
            {
                "id": "1",
                "name": "Mark",
                "description": "A graphic artist",
                "role": "admin",
                "picture_url": "example.com",
                "team_type": "Executive",
                "facebook_link": "facebook.com/mark",
                "instagram_link": "instagram.com/mark",
                "xtwitter_link": "twitter.com/mark"
            },
            {
                "id": "2",
                "name": "John",
                "description": "A software developer",
                "role": "developer",
                "picture_url": "example2.com",
                "team_type": "Development",
                "facebook_link": "facebook.com/john",
                "instagram_link": "instagram.com/john",
                "xtwitter_link": "twitter.com/john"
            }
        ]

        with patch('api.v1.services.team.TeamServices.fetch_all') as mock_fetch_all:
            mock_fetch_all.return_value = test_members

            response = client.get("/api/v1/team/members")
            assert response.status_code == 200
            assert response.json()['message'] == "Team members retrieved successfully"
            assert response.json()['data'] == test_members
            assert response.json()['success'] == True

    # Handling case where no team members are found
    def test_get_all_team_members_empty(self, client):
        with patch('api.v1.services.team.TeamServices.fetch_all') as mock_fetch_all:
            mock_fetch_all.return_value = []

            response = client.get("/api/v1/team/members")
            assert response.status_code == 404
            assert response.json()['message'] == 'No team members found'

    # Handling unauthorized request
    def test_get_all_team_members_unauthorized(self, client):
        app.dependency_overrides = {}

        response = client.get("/api/v1/team/members")
        assert response.status_code == 401
        assert response.json()['message'] == 'Not authenticated'

    # Handling forbidden request
    def test_get_all_team_members_forbidden(self, client):
        app.dependency_overrides = {}
        app.dependency_overrides[get_db] = mock_db
        app.dependency_overrides[oauth2_scheme] = mock_oauth

        with patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_super_admin=False)) as cu:
            response = client.get("/api/v1/team/members")
        assert response.status_code == 403
        assert response.json()['message'] == 'You do not have permission to access this resource'
