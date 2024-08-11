import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import calendar

from api.v1.services.analytics import AnalyticsServices
from api.v1.schemas.analytics import AnalyticsChartsResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@pytest.fixture
def mock_db():
    """
    Mock db
    """
    with patch("api.v1.services.analytics.get_db", return_value=MagicMock(spec=Session)) as mock:
        yield mock

@pytest.fixture
def mock_user_service():
    """
    Mock user_service
    """
    with patch("api.v1.services.user.user_service.get_current_user") as mock:
        yield mock

@pytest.fixture
def mock_oauth2_scheme():
    """
    Mock oauth2 scheme
    """
    with patch("api.v1.services.user.oauth2_scheme", return_value="test_token") as mock:
        yield mock

def test_get_analytics_line_chart_super_admin(mock_db, mock_user_service, mock_oauth2_scheme):
    """
    Test get analytics line_chart_data for super_admin
    """
    # Arrange
    mock_user = MagicMock()
    mock_user.is_superadmin = True
    mock_user_service.return_value = mock_user

    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    analytics_service = AnalyticsServices()

    # Act
    response = analytics_service.get_analytics_line_chart(token="test_token", db=mock_db)

    # Assert
    assert isinstance(response, AnalyticsChartsResponse)
    assert response.status == "success"
    assert response.data is not None

def test_get_analytics_line_chart_non_super_admin(mock_db, mock_user_service, mock_oauth2_scheme):
    """
    Test get analytics_line_chart_data for non super_admin with organisation
    """
    # Arrange
    mock_user = MagicMock()
    mock_user.is_superadmin = False
    mock_user_service.return_value = mock_user

    mock_user_organisation = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user_organisation

    analytics_service = AnalyticsServices()

    # Act
    response = analytics_service.get_analytics_line_chart(token="test_token", db=mock_db)

    # Assert
    assert isinstance(response, AnalyticsChartsResponse)
    assert response.status == "success"
    assert response.data is not None

def test_get_analytics_line_chart_no_org(mock_db, mock_user_service, mock_oauth2_scheme):
    """
    Test get analytics_line_chart_data for non super_admin without organisation
    """
    # Arrange
    mock_user = MagicMock()
    mock_user.is_superadmin = False
    mock_user_service.return_value = mock_user

    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    analytics_service = AnalyticsServices()

    # Act
    response = analytics_service.get_analytics_line_chart(token="test_token", db=mock_db)

    # Assert
    assert isinstance(response, AnalyticsChartsResponse)
    assert response.status == "success"
    assert response.data == {month: 0 for month in calendar.month_name if month}
