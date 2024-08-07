import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from api.v1.routes.analytics import get_analytics_summary
from api.v1.services.analytics import AnalyticsServices
from api.v1.schemas.analytics import AnalyticsSummaryResponse, MetricData
from main import app
from api.db.database import get_db


client = TestClient(app)


@pytest.fixture
def mock_analytics_service(mocker):
    mock = mocker.patch(
        'api.v1.services.analytics.AnalyticsServices', autospec=True)
    mock.get_analytics_summary = mocker.Mock()
    return mock


@pytest.fixture
def mock_oauth2_scheme(mocker):
    return mocker.patch('api.v1.services.user.oauth2_scheme', return_value="test_token")


@pytest.fixture
def mock_get_current_user_super_admin(mocker):
    return mocker.patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_super_admin=True, id="super_admin_id"))


@pytest.fixture
def mock_get_current_user_user(mocker):
    return mocker.patch('api.v1.services.user.user_service.get_current_user', return_value=MagicMock(is_super_admin=False, id="user_id", organization_id="org_id"))


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    with patch("api.v1.services.user.get_db", autospec=True) as mock_get_db:
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        yield mock_db
    app.dependency_overrides = {}


def test_analytics_summary_super_admin(mock_analytics_service, mock_oauth2_scheme, mock_get_current_user_super_admin, mock_db_session):
    expected_response = AnalyticsSummaryResponse(
        message="Successfully retrieved summary for super admin dashboard",
        status='success',
        status_code=200,
        data=[
                {'total_revenue': MetricData(
                    value=10000, percentage_increase=10)},
                {'total_products': MetricData(
                    value=50, percentage_increase=5)},
                {'total_users': MetricData(value=200, percentage_increase=2)},
                {'lifetime_sales': MetricData(
                    value=50000, percentage_increase=8)}
        ]
    )


    token = "superadmin_token"
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()

    response = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": start_date.isoformat(
        ), "end_date": end_date.isoformat()}
    )

    assert response.status_code == 200
    


def test_analytics_summary_user(mock_analytics_service, mock_oauth2_scheme, mock_get_current_user_user, mock_db_session):
    expected_response = AnalyticsSummaryResponse(
        message="Successfully retrieved summary for user dashboard",
        status='success',
        status_code=200,
        data=[
            {'total_revenue': MetricData(value=5000, percentage_increase=15)},
            {'subscriptions': MetricData(value=100, percentage_increase=10)},
            {'sales': MetricData(value=150, percentage_increase=5)},
            {'active_now': MetricData(value=25, percentage_increase=2)}
        ]
    )

    token = "user_token"
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()

    response = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token}"},
        params={"start_date": start_date.isoformat(
        ), "end_date": end_date.isoformat()}
    )

    assert response.status_code == 200
    


def test_analytics_summary_no_dates(mock_analytics_service, mock_oauth2_scheme, mock_get_current_user_user, mock_db_session):
    expected_response = AnalyticsSummaryResponse(
        message="Successfully retrieved summary for user dashboard",
        status='success',
        status_code=200,
        data=[
            {'total_revenue': MetricData(value=3000, percentage_increase=8)},
            {'subscriptions': MetricData(value=75, percentage_increase=12)},
            {'sales': MetricData(value=120, percentage_increase=4)},
            {'active_now': MetricData(value=20, percentage_increase=3)}
        ]
    )


    token = "user_token"

    response = client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    
