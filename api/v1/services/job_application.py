from fastapi import HTTPException
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
from api.v1.schemas.job_application import JobApplicationBase, JobApplicationData
from api.utils.success_response import success_response

class JobApplicationService(Service):
    """Job applications service functionality"""

    def create():
        pass

    def fetch():
        pass

    def fetch_all(
        self, job_id: str, page: int, per_page: int, db: Annotated[Session, get_db]
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
        application_data = JobApplicationData(
            page=page, per_page=per_page, total_pages=total_pages, applications=application_schema
        )

        return success_response(
            status_code=200,
            message="Successfully fetched job applications",
            data=application_data
        )

        

    def update():
        pass

    def delete():
        pass

job_application_service = JobApplicationService()

