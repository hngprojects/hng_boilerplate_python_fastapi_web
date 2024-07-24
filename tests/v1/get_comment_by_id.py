import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from uuid_extensions import uuid7

from api.db.database import get_db
from api.v1.models.blog import Blog
from api.v1.models.user import User

from ...main import app
from api.v1.models.comment import Comment


# Mock database dependency
@pytest.fixture
def db_session():
    db_session = MagicMock(spec=Session)
    return db_session


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


def test_get_comment_not_found(client, db_session):
    comment_id = "yeuiw36"

    response = client.get(f"/comments/{comment_id}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Not Found",
    }