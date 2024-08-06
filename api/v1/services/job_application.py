"""
Job applications services
"""
from typing import Annotated
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.job import JobApplication
from api.core.base.services import Service
from api.v1.schemas.job_application import (SingleJobAppResponse,
                                            JobApplicationBase)


class JobApplicationService(Service):
    """
    Job application service class
    """
    def create(self):
        pass

    def fetch(self, job_id:str, application_id: str,
              db: Annotated[Session, Depends(get_db)]):
        """
        Fetch a single job application.
        Args:
            job_id: The id of the job for the applicant
            application_id: The id of the application for the job
            db: database Session object
        Returne:
            SingleJobAppResponse: Response on success
        """
        application: object | None = db.query(JobApplication).filter_by(job_id=job_id,
                                                                        id=application_id).first()
        if not application:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Invalid id')
        else:
            return SingleJobAppResponse(status='success',
                                      status_code=status.HTTP_200_OK,
                                      message='successfully retrieved job application.',
                                      data=JobApplicationBase.model_validate(application,
                                                                             from_attributes=True))

    def fetch_all(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

job_application_service = JobApplicationService()