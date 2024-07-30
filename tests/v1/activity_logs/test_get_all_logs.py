from main import app
from api.db.database import get_db
from api.v1.models.activity_logs import ActivityLog
from uuid_extensions import uuid7
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


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


def test_get_all_activity_logs_empty(client, db_session_mock):

    db_session_mock.query().filter().all.return_value = []

    response = client.get("/api/v1/activity-logs/")

    assert response.status_code == 200


def test_get_all_activity_logs_with_data(client, db_session_mock):
    log_id = str(uuid7())
    user_id = str(uuid7())
    timezone_offset = -8.0
    tzinfo = timezone(timedelta(hours=timezone_offset))
    timeinfo = datetime.now(tzinfo)
    created_at = timeinfo
    updated_at = timeinfo

    activity_log = ActivityLog(
        id=log_id,
        user_id=user_id,
        action="profile Update",
        timestamp=timeinfo,
        created_at=created_at,
        updated_at=updated_at
    )

    db_session_mock.query().filter().all.return_value = [activity_log]

    response = client.get("/api/v1/activity-logs/")

    assert response.status_code == 200
