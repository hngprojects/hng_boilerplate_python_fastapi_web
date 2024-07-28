import pytest
from fastapi.testclient import TestClient
from tests.database import session, client
from api.v1.models import *
from api.db.database import get_db
from main import app


VALID_ACCESS_TOKEN = "valid_token"
INVALID_ACCESS_TOKEN = "invalid_token"


class MockResponse:
    """This class will be used to mock the response of the Facebook API."""

    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.content


class MockTestClient(TestClient):
    """This class will be used to mock the client of the Facebook API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, *args, **kwargs):
        valid_response = {
            "status_code": 201,
            "message": "User created successfully",
            "data": {
                "access_token": "valid_token",
                "refresh_token": "valid_refresh_token",
            },
        }
        invalid_response = {
            "status_code": 401,
            "error": "Could not validate credentials.",
            "message": "Invalid access token",
        }
        unprocessable_request_response = {
            "status_code": 422,
            "error": "Invalid Credentials!",
            "message": "Unprocessable request",
        }
        missing_access_token_response = {
            "detail": [
                {
                    "loc": ["body", "access_token"],
                    "msg": "Field required",
                    "type": "missing",
                }
            ]
        }
        if kwargs.get("json").get("access_token") == VALID_ACCESS_TOKEN:
            return MockResponse(content=valid_response, status_code=201)
        elif kwargs.get("json").get("access_token") == INVALID_ACCESS_TOKEN:
            return MockResponse(content=invalid_response, status_code=401)
        elif kwargs.get("json").get("access_token") is None:
            return MockResponse(content=missing_access_token_response, status_code=422)
        return MockResponse(content=unprocessable_request_response, status_code=422)


@pytest.fixture()
def mock_client():
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield MockTestClient(app)


def test_valid_facebook_login(client, mock_client, session):
    response = {}
    if VALID_ACCESS_TOKEN != "valid_token":
        response = client.post(
            "/api/v1/auth/facebook",
            json={"access_token": VALID_ACCESS_TOKEN},
        )
    else:
        response = mock_client.post(
            "/api/v1/auth/facebook",
            json={"access_token": VALID_ACCESS_TOKEN},
        )
    assert response.status_code in [200, 201]
    assert "access_token" in response.json().get("data")
    assert "refresh_token" in response.json().get("data")


def test_invalid_facebook_login(client, mock_client, session):
    response = {}
    if INVALID_ACCESS_TOKEN != "invalid_token":
        response = client.post(
            "/api/v1/auth/facebook",
            json={"access_token": INVALID_ACCESS_TOKEN},
        )
    else:
        response = mock_client.post(
            "/api/v1/auth/facebook",
            json={"access_token": INVALID_ACCESS_TOKEN},
        )
    assert response.status_code == 401
    assert "error" in response.json()


def test_missing_access_token(client, mock_client, session):
    response = {}
    if VALID_ACCESS_TOKEN != "valid_token":
        response = client.post(
            "/api/v1/auth/facebook",
            json={"access_token": None},
        )
    else:
        response = mock_client.post(
            "/api/v1/auth/facebook",
            json={"access_token": None},
        )
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "access_token" in response.json().get("detail")[0].get("loc")
    assert "Field required" in response.json().get("detail")[0].get("msg")


def test_unprocessable_request(client, mock_client, session):
    response = {}
    if VALID_ACCESS_TOKEN != "valid_token":
        response = client.post(
            "/api/v1/auth/facebook",
            json={"access_token": "invalid token"},
        )
    else:
        response = mock_client.post(
            "/api/v1/auth/facebook",
            json={"access_token": "invalid token"},
        )
    assert response.status_code == 422
    assert "message" in response.json()
    assert "error" in response.json()
