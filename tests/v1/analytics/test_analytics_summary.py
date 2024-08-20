import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from api.v1.routes.dashboard import get_analytics_summary
from api.v1.services.analytics import AnalyticsServices
from api.v1.schemas.analytics import AnalyticsSummaryResponse
from main import app
from api.db.database import get_db


client = TestClient(app)


@pytest.fixture
def mock_analytics_service(mocker):
    mock = mocker.patch(
        'api.v1.services.analytics.AnalyticsServices', autospec=True)
    mock.get_summary_data_super_admin = mocker.Mock()
    mock.get_summary_data_organisation = mocker.Mock()
    return mock


@pytest.fixture
def mock_oauth2_scheme(mocker):
    return mocker.patch('api.v1.services.user.oauth2_scheme', return_value="test_token")


@pytest.fixture
def mock_get_current_user_super_admin(mocker):
    return mocker.patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_superadmin=True, id="super_admin_id"))


@pytest.fixture
def mock_get_current_user_user(mocker):
    return mocker.patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_superadmin=False, id="user_id", organisation_id="org_id"))

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


def test_statistics_summary_super_admin(mock_analytics_service, mock_oauth2_scheme, mock_get_current_user_super_admin, mock_db_session):
    expected_response = AnalyticsSummaryResponse(
        message="Admin Statistics Fetched",
        status='success',
        status_code=200,
        data={
            "total_revenue": {
                "current_month": 10000,
                "previous_month": 9000,
                "percentage_difference": "11.11%"
            },
            "total_users": {
                "current_month": 200,
                "previous_month": 180,
                "percentage_difference": "11.11%"
            },
            "total_products": {
                "current_month": 50,
                "previous_month": 45,
                "percentage_difference": "11.11%"
            },
            "lifetime_sales": {
                "current_month": 50000,
                "previous_month": 45000,
                "percentage_difference": "11.11%"
            }
        }
    )

    token = "superadmin_token"
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()

    response = client.get(
        "/api/v1/dashboard/statistics",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": "2024-07-09T00:00:00",
                "end_date": "2024-08-08T00:00:00"}
    )

    assert response.status_code == 200


def test_statistics_summary_user(mock_analytics_service, mock_oauth2_scheme, mock_get_current_user_user, mock_db_session):
    expected_response = AnalyticsSummaryResponse(
        message="User Statistics Fetched",
        status='success',
        status_code=200,
        data={
            "revenue": {
                "current_month": 5000,
                "previous_month": 4500,
                "percentage_difference": "11.11%"
            },
            "subscriptions": {
                "current_month": 100,
                "previous_month": 90,
                "percentage_difference": "11.11%"
            },
            "orders": {
                "current_month": 150,
                "previous_month": 135,
                "percentage_difference": "11.11%"
            },
            "active_users": {
                "current": 25,
                "difference_an_hour_ago": 13
            }
        }
    )

    token = "user_token"
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()

    response = client.get(
        "/api/v1/dashboard/statistics",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": "2024-07-09T00:00:00",
                "end_date": "2024-08-08T00:00:00"}
    )

    assert response.status_code == 200


def test_statistics_summary_no_dates(mock_analytics_service, mock_oauth2_scheme, mock_get_current_user_user, mock_db_session):
    expected_response = AnalyticsSummaryResponse(
        message="User Statistics Fetched",
        status='success',
        status_code=200,
        data={
            "revenue": {
                "current_month": 3000,
                "previous_month": 2700,
                "percentage_difference": "11.11%"
            },
            "subscriptions": {
                "current_month": 75,
                "previous_month": 67,
                "percentage_difference": "11.94%"
            },
            "orders": {
                "current_month": 120,
                "previous_month": 108,
                "percentage_difference": "11.11%"
            },
            "active_users": {
                "current": 25,
                "difference_an_hour_ago": 11
            }
        }
    )

    token = "user_token"

    response = client.get(
        "/api/v1/dashboard/statistics",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
