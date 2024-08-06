from typing import Any, Optional
from fastapi import HTTPException, Depends, status
from typing import Annotated
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.core.base.services import Service
from api.v1.models.job import JobApplication
from api.v1.schemas.job_application import CreateJobApplication, UpdateJobApplication


class JobApplicationService(Service):
    '''Job application service functionality'''

    def create(self, db: Session, job_id: str, schema: CreateJobApplication):
        """Create a new job application"""

        job_application = JobApplication(**schema.model_dump(), job_id=job_id)

        # Check if user has already applied by checking through the email
        if db.query(JobApplication).filter(
            JobApplication.applicant_email == schema.applicant_email,
            JobApplication.job_id == job_id,
        ).first():
            raise HTTPException(
                status_code=400, detail='You have already applied for this role')

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
                    query = query.filter(
                        getattr(JobApplication, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, job_id: str, application_id: str):
        """Fetches a, FAQ by id"""

        job_application = db.query(JobApplication).filter(
            JobApplication.id == application_id,
            JobApplication.job_id == job_id,
        ).first()

        if not job_application:
            raise HTTPException(
                status_code=404, detail='Job application not found')

        return job_application

    def update(self, db: Session, job_id: str, application_id: str, schema: UpdateJobApplication):
        """Updates an application"""

        job_application = self.fetch(
            db=db, job_id=job_id, application_id=application_id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            setattr(job_application, key, value)

        db.commit()
        db.refresh(job_application)
        return job_application

    def delete(self, job_id: str, application_id: str,
               db: Annotated[Session, Depends(get_db)]):
        """
        Delete a single job application.
        Args:
            job_id: The id of the job for the applicant
            application_id: The id of the application for the job
            db: database Session object
        Returns:
            None
        """
        application: object | None = db.query(JobApplication).filter_by(job_id=job_id,
                                                                        id=application_id).first()
        if not application:
            raise HTTPException(
                status_code=404, detail='Invalid id')
        db.delete(application)
        db.commit()


job_application_service = JobApplicationService()
