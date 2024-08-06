from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from api.v1.services.user import user_service
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.job_application import JobApplicationResponse
from api.v1.services.job_application import job_application_service

job_application = APIRouter(prefix="/jobs/{job_id}/applications", tags=["Job Applications"])

@job_application.get("", response_model=JobApplicationResponse, status_code=status.HTTP_200_OK,)
async def fetch_all_job_applications(
    job_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
    per_page: Annotated[int, Query(ge=1, description="Number of applications per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 1,
):
    """Superadmin endpoint to fetch all applications for a job

    Args:
        - job_id (str): The Job ID
        - db (Annotated[Session, Depends): the database session
        - current_user: The current authenticated super admin 
        - per_page: Number of customers per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)

    Returns:
        obj: paginated list of applications for the Job ID

    Raises:
        - HTTPException: 403 FORBIDDEN (Current user is not a super admin)
        - HTTPException: 404 NOT FOUND (Provided Job ID does not exist)
    """
    return job_application_service.fetch_all(job_id=job_id, page=page, per_page=per_page,db=db)
