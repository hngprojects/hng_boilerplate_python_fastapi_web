from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.comment import Comment, CommentLike
from typing import Any, Optional, Union, Annotated
from sqlalchemy import desc
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.utils.db_validators import check_model_existence
from api.utils.pagination import paginated_response
from api.v1.models.job import Job, JobApplication
from api.utils.success_response import success_response
from api.v1.schemas.job_application import (SingleJobAppResponse,
                                            JobApplicationBase,
                                            JobApplicationData,
                                            JobApplicationResponseData,
                                            CreateJobApplication, UpdateJobApplication
                                            )

class JobApplicationService(Service):
    """
    Job application service class
    """

    def fetch(self, job_id: str, application_id: str,
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
            raise HTTPException(
                status_code=400, detail='You have already applied for this role')

        db.add(job_application)
        db.commit()
        db.refresh(job_application)

        return job_application

    def fetch_all(
        self, job_id: str, page: int, per_page: int, db: Annotated[Session, Depends(get_db)]
    ):
        """Fetches all applications for a job 

        Args:
            job_id: the Job ID of the applications
            page: the number of the current page
            per_page: the page size for a current page
            db: Database Session object
        Returns:
            Response: An exception if error occurs
            object: Response object containing the applications
        """

        # check if job id exists
        check_model_existence(db, Job, job_id)

        # Calculating offset value from page number and per-page given
        offset_value = (page - 1) * per_page

        # Querying the db for applications of that job
        applications = db.query(JobApplication).filter_by(job_id=job_id).offset(offset_value).limit(per_page).all()

        total_applications = len(applications)

        # Total pages: integer division with ceiling for remaining items
        total_pages = int(total_applications / per_page) + (total_applications % per_page > 0)

        application_schema: list = [
            JobApplicationBase.model_validate(application) for application in applications
        ]
        application_data = JobApplicationResponseData(
            page=page, per_page=per_page, total_pages=total_pages, applications=application_schema
        )

        return success_response(
            status_code=200,
            message="Successfully fetched job applications",
            data=application_data
        )

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
