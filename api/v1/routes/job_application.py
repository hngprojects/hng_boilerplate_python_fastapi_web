"""
job_application routes
"""
from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session
from typing import Annotated

from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.services.job_application import job_application_service

job_application = APIRouter(prefix='/jobs/{job_id}/applications', tags=['Job Applications'])


@job_application.get('/{application_id}', status_code=status.HTTP_200_OK)
async def get_single_application(job_id: str,
                                 application_id: str,
                                 db: Annotated[Session, Depends(get_db)],
                                 current_user : Annotated[User , Depends(user_service.get_current_super_admin)]):
    """
    Retrieves a single application.


    Args:
        job_id: The id of the job for the applicant
        application_id: The id of the application for the job
        db: database Session object
        current_user: the super admin user
    Returns:
        SingleJobAppResponse: response on success
    """
    return job_application_service.fetch(job_id, application_id, db)
