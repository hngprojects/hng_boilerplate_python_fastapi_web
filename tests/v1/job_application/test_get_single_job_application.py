import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.v1.services.job_application import JobApplicationService
from api.v1.models.job import JobApplication
from api.v1.schemas.job_application import (SingleJobAppResponse,
                                            JobApplicationData)


# Sample data to be used in tests
mock_application_data = {
    'job_id': '123',
    'applicant_name': 'John Doe',
    'applicant_email': 'john.doe@example.com',
    'resume_link': 'http://resume.com',
    'portfolio_link': 'http://portfolio.com',
    'cover_letter': 'Cover letter content',
    'application_status': 'pending'
}

# Create a mock job application object
def create_mock_application():
    mock_app = MagicMock(spec=JobApplication)
    for key, value in mock_application_data.items():
        setattr(mock_app, key, value)
    return mock_app


@pytest.fixture
def mock_db_session():
    """Fixture to mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def job_application_service():
    """Fixture to create an instance of JobApplicationService"""
    return JobApplicationService()


def test_fetch_success(job_application_service, mock_db_session):
    """
    test for successful retrieval of single application
    """
    # Setup mock
    mock_application = create_mock_application()
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_application

    job_id = '123'
    application_id = '456'
    
    # Call the fetch method
    result = job_application_service.fetch(job_id, application_id, mock_db_session)
    
    # Validate result
    expected_response = SingleJobAppResponse(
        status='success',
        status_code=status.HTTP_200_OK,
        message='successfully retrieved job application.',
        data=JobApplicationData(**mock_application_data)
    )
    
    assert result == expected_response


def test_fetch_not_found(job_application_service, mock_db_session):
    """
    Test for unsuccessful job application retrieval
    """
    # Setup mock to return None
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

    job_id = '123'
    application_id = '456'
    
    # Expect HTTPException to be raised
    with pytest.raises(HTTPException) as excinfo:
        job_application_service.fetch(job_id, application_id, mock_db_session)
    
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == 'Invalid id'
