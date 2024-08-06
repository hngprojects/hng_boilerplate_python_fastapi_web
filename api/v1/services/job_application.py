
"""
Job applications services
"""
from typing import Annotated, Any, Optional
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.job import JobApplication
from api.core.base.services import Service
from api.v1.schemas.job_application import (SingleJobAppResponse,
                                            JobApplicationBase,
                                            JobApplicationData,
                                           CreateJobApplication, UpdateJobApplication
                                           )


class JobApplicationService(Service):
    """
    Job application service class
    """

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
                                      data=JobApplicationData.model_validate(application,
                                                                             from_attributes=True))                                   

    def create(self, db: Session, job_id: str, schema: CreateJobApplication):
        """Create a new job application"""

        job_application = JobApplication(**schema.model_dump(), job_id=job_id)

        # Check if user has already applied by checking through the email
        if db.query(JobApplication).filter(
            JobApplication.applicant_email == schema.applicant_email,
            JobApplication.job_id == job_id,
        ).first():
            raise HTTPException(status_code=400, detail='You have already applied for this role')
        
        db.add(job_application)
        db.commit()
        db.refresh(job_application)

        return job_application

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all applications with option to search using query parameters"""

        query = db.query(JobApplication)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(JobApplication, column) and value:
                    query = query.filter(getattr(JobApplication, column).ilike(f"%{value}%"))

        return query.all()

        
    def update(self, db: Session, job_id: str, application_id: str, schema: UpdateJobApplication):
        """Updates an application"""

        job_application = self.fetch(db=db, job_id=job_id, application_id=application_id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            setattr(job_application, key, value)

        db.commit()
        db.refresh(job_application)
        return job_application

    def delete(self, db: Session, job_id: str, application_id: str):
        """Deletes an FAQ"""

        faq = self.fetch(db=db, job_id=job_id, application_id=application_id)
        db.delete(faq)
        db.commit()


job_application_service = JobApplicationService()

