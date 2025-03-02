import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.v1.schemas.feature_request import FeatureRequestCreate, FeatureRequestResponse, FeatureRequestUpdate
from api.v1.routes.feature_request import create_feature_request, get_feature_requests, get_feature_request, update_feature_request, delete_feature_request


@pytest.fixture
def db_session():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_user():
    """Sample regular user"""
    user = MagicMock()
    user.id = str(uuid.uuid4())
    user.is_superadmin = False
    return user


@pytest.fixture
def admin_user():
    """Sample admin user"""
    user = MagicMock()
    user.id = str(uuid.uuid4())
    user.is_superadmin = True
    return user


@pytest.fixture
def feature_request_data():
    """Sample feature request data for testing"""
    return FeatureRequestCreate(
        title="Test Feature",
        description="This is a test feature request",
        priority="Low"  # Changed from int to string
    )


@pytest.fixture
def feature_request_response():
    """Sample feature request response for testing"""
    return FeatureRequestResponse(
        id=str(uuid.uuid4()),
        title="Test Feature",
        description="This is a test feature request",
        priority="Low",  # Changed from int to string
        status="Pending",
        user_id=str(uuid.uuid4()),
        created_at="2025-03-01T12:00:00",
        updated_at="2025-03-01T12:00:00"
    )


class TestCreateFeatureRequest:
    @patch("api.v1.services.feature_request.FeatureRequestService.create_feature_request")
    def test_create_feature_request_success(self, mock_create, db_session, sample_user, feature_request_data):
        # Arrange
        mock_create.return_value = FeatureRequestResponse(
            id=str(uuid.uuid4()),
            title=feature_request_data.title,
            description=feature_request_data.description,
            priority=feature_request_data.priority,
            status="Pending",
            user_id=sample_user.id,
            created_at="2025-03-01T12:00:00",
            updated_at="2025-03-01T12:00:00"
        )
        
        # Act
        result = create_feature_request(feature_request_data, db_session, sample_user)
        
        # Assert
        mock_create.assert_called_once_with(
            db_session, feature_request_data, sample_user.id
        )
        assert result.title == feature_request_data.title
        assert result.description == feature_request_data.description
        assert result.priority == feature_request_data.priority
        assert result.status == "Pending"  # Verify status is Pending
        assert result.user_id == sample_user.id


class TestGetFeatureRequests:
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_requests")
    def test_get_feature_requests_as_admin(self, mock_get, db_session, admin_user):
        # Arrange
        mock_get.return_value = [
            FeatureRequestResponse(
                id=str(uuid.uuid4()),
                title="Feature 1",
                description="Description 1",
                priority="High",  # Changed from int to string
                status="Pending",
                user_id=str(uuid.uuid4()),
                created_at="2025-03-01T12:00:00",
                updated_at="2025-03-01T12:00:00"
            ),
            FeatureRequestResponse(
                id=str(uuid.uuid4()),
                title="Feature 2",
                description="Description 2",
                priority="Medium",  # Changed from int to string
                status="Approved",
                user_id=str(uuid.uuid4()),
                created_at="2025-03-01T12:00:00",
                updated_at="2025-03-01T12:00:00"
            )
        ]
        
        # Act
        result = get_feature_requests(0, 10, db_session, admin_user)
        
        # Assert
        mock_get.assert_called_once_with(db_session, 0, 10)
        assert len(result) == 2
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_user_feature_requests")
    def test_get_feature_requests_as_regular_user(self, mock_get_user, db_session, sample_user):
        # Arrange
        mock_get_user.return_value = [
            FeatureRequestResponse(
                id=str(uuid.uuid4()),
                title="User Feature",
                description="User Description",
                priority="Low",  # Changed from int to string
                status="Pending",
                user_id=sample_user.id,
                created_at="2025-03-01T12:00:00",
                updated_at="2025-03-01T12:00:00"
            )
        ]
        
        # Act
        result = get_feature_requests(0, 10, db_session, sample_user)
        
        # Assert
        mock_get_user.assert_called_once_with(db_session, sample_user.id, 0, 10)
        assert len(result) == 1
        assert result[0].user_id == sample_user.id


class TestGetFeatureRequest:
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_get_feature_request_not_found(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        mock_get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_feature_request(feature_request_id, db_session, sample_user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Feature request not found"
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_get_feature_request_forbidden(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        other_user_id = str(uuid.uuid4())
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = other_user_id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_feature_request(feature_request_id, db_session, sample_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not authorized to access this feature request"
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_get_feature_request_success_owner(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = sample_user.id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act
        result = get_feature_request(feature_request_id, db_session, sample_user)
        
        # Assert
        assert result == mock_feature_request
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_get_feature_request_success_admin(self, mock_get_by_id, db_session, admin_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        other_user_id = str(uuid.uuid4())
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = other_user_id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act
        result = get_feature_request(feature_request_id, db_session, admin_user)
        
        # Assert
        assert result == mock_feature_request


class TestUpdateFeatureRequest:
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_update_feature_request_not_found(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        update_data = FeatureRequestUpdate(title="Updated Title")
        mock_get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_feature_request(feature_request_id, update_data, db_session, sample_user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Feature request not found"
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_update_feature_request_forbidden(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        update_data = FeatureRequestUpdate(title="Updated Title")
        other_user_id = str(uuid.uuid4())
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = other_user_id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_feature_request(feature_request_id, update_data, db_session, sample_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not authorized to update this feature request"

    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_update_status_forbidden_for_regular_user(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        update_data = FeatureRequestUpdate(status="Approved")  # Try to update status
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = sample_user.id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_feature_request(feature_request_id, update_data, db_session, sample_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Only admins can update the status field"

    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    @patch("api.v1.services.feature_request.FeatureRequestService.update_feature_request")
    def test_update_status_allowed_for_admin(self, mock_update, mock_get_by_id, db_session, admin_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        update_data = FeatureRequestUpdate(status="Approved")  # Admin updating status
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = str(uuid.uuid4())  # Different user's request
        
        updated_feature_request = FeatureRequestResponse(
            id=feature_request_id,
            title="Original Title",
            description="Original Description",
            priority="medium",
            status="Approved",  # Status successfully updated
            user_id=mock_feature_request.user_id,
            created_at="2025-03-01T12:00:00",
            updated_at="2025-03-01T12:30:00"
        )
        
        mock_get_by_id.return_value = mock_feature_request
        mock_update.return_value = updated_feature_request

        # Act
        result = update_feature_request(feature_request_id, update_data, db_session, admin_user)
        
        # Assert
        mock_update.assert_called_once_with(
            db_session, feature_request_id, update_data
        )
        assert result.status == "Approved"  # Status was updated
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    @patch("api.v1.services.feature_request.FeatureRequestService.update_feature_request")
    def test_update_feature_request_success(self, mock_update, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        update_data = FeatureRequestUpdate(title="Updated Title")
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = sample_user.id
        
        updated_feature_request = FeatureRequestResponse(
            id=feature_request_id,
            title="Updated Title",
            description="Original Description",
            priority="Medium",  # Changed from int to string
            status="Pending",  # Status unchanged
            user_id=sample_user.id,
            created_at="2025-03-01T12:00:00",
            updated_at="2025-03-01T12:30:00"
        )
        
        mock_get_by_id.return_value = mock_feature_request
        mock_update.return_value = updated_feature_request
        
        # Act
        result = update_feature_request(feature_request_id, update_data, db_session, sample_user)
        
        # Assert
        mock_update.assert_called_once_with(
            db_session, feature_request_id, update_data
        )
        assert result.title == "Updated Title"
        assert result.user_id == sample_user.id
        assert result.status == "Pending"  # Status remains unchanged


class TestDeleteFeatureRequest:
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_delete_feature_request_not_found(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        mock_get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_feature_request(feature_request_id, db_session, sample_user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Feature request not found"
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    def test_delete_feature_request_forbidden(self, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        other_user_id = str(uuid.uuid4())
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = other_user_id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_feature_request(feature_request_id, db_session, sample_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not authorized to delete this feature request"
        
    @patch("api.v1.services.feature_request.FeatureRequestService.get_feature_request_by_id")
    @patch("api.v1.services.feature_request.FeatureRequestService.delete_feature_request")
    def test_delete_feature_request_success(self, mock_delete, mock_get_by_id, db_session, sample_user):
        # Arrange
        feature_request_id = str(uuid.uuid4())
        
        mock_feature_request = MagicMock()
        mock_feature_request.user_id = sample_user.id
        
        mock_get_by_id.return_value = mock_feature_request
        
        # Act
        result = delete_feature_request(feature_request_id, db_session, sample_user)
        
        # Assert
        mock_delete.assert_called_once_with(db_session, feature_request_id)
        assert result is None
