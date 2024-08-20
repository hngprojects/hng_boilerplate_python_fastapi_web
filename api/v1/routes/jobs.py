#!/usr/bin/env python3

from api.utils.success_response import success_response
from api.v1.schemas.jobs import PostJobSchema, AddJobSchema, JobCreateResponseSchema, UpdateJobSchema
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status, Query

from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.utils.logger import logger
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.job import Job, JobApplication
from api.v1.services.jobs import job_service
from api.v1.services.job_application import job_application_service, UpdateJobApplication
from api.utils.pagination import paginated_response
from api.utils.db_validators import check_model_existence
import uuid
from api.v1.schemas.job_application import CreateJobApplication, UpdateJobApplication, JobApplicationResponse


jobs = APIRouter(prefix="/jobs", tags=["Jobs"])


@jobs.post(
    "",
    response_model=success_response,
    status_code=201,

)
async def add_jobs(
    job: PostJobSchema,
    db: Session = Depends(get_db),
    admin: User = Depends(user_service.get_current_super_admin),
):
    """
    Add a job listing to the database.
    This endpoint allows an admin to post a job listing to the database.

    Parameters:
    - job: PostJobSchema
        The details of the job listing.
    - admin: User (Depends on get_current_super_admin)
        The current admin posting the job request. This is a dependency that provides the admin context.
    - db: The database session
    """
    if job.title.strip() == "" or job.description.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid request data")

    job_full = AddJobSchema(author_id=admin.id, **job.model_dump())
    new_job = job_service.create(db, job_full)
    logger.info(f"Job Listing created successfully {new_job.id}")

    return success_response(
        message="Job listing created successfully",
        status_code=201,
        data=jsonable_encoder(JobCreateResponseSchema.model_validate(new_job))
    )


@jobs.get("/{job_id}", response_model=success_response)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve job details by ID.
    This endpoint fetches the details of a specific job by its ID.

    Parameters:
    - job_id: str
        The ID of the job to retrieve.
    - db: The database session
    """
    job = job_service.fetch(db, job_id)

    return success_response(
        message="Retrieved Job successfully",
        status_code=200,
        data=jsonable_encoder(job)
    )


@jobs.get("")
async def fetch_all_jobs(
    db: Session = Depends(get_db),
):
    """
        Description
                Get endpoint for unauthenticated users to retrieve all jobs.

        Args:
                db: the database session object

        Returns:
                Response: a response object containing details if successful or appropriate errors if not
    """
    jobs = job_service.fetch_all(db)
    return success_response(
       status_code=status.HTTP_200_OK,
       data=jsonable_encoder(jobs),
       message="Jobs Successfully Fetched!"
    )


@jobs.delete(
    "/{job_id}",
    response_model=success_response,
    status_code=200,

)
async def delete_job_by_id(
    job_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(user_service.get_current_super_admin),
):
    """
    Delete a job record by id
    """
    job_service.delete(db, job_id)

    return success_response(
        message="Job listing deleted successfully",
        status_code=200,
    )


@jobs.patch("/{id}")
async def update_job(
    id: str,
    schema: UpdateJobSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    '''This endpoint is to update a job listing by its id'''

    job = job_service.update(db, id=id, schema=schema)

    return success_response(
        data=jsonable_encoder(job),
        message="Successfully updated a job listing",
        status_code=status.HTTP_200_OK,
    )


# -------------------- JOB APPLICATION ROUTES ------------------------
# --------------------------------------------------------------------

@jobs.post("/{job_id}/applications", response_model=success_response)
async def apply_to_job(
    job_id: str,
    application: CreateJobApplication,
    db: Session = Depends(get_db)
):
    '''Endpoint to apply for a job'''

    job_application = job_application_service.create(
        db=db, schema=application, job_id=job_id)

    return success_response(
        status_code=201,
        message="Job application submitted successfully",
        data=jsonable_encoder(job_application)
    )


@jobs.patch("/{job_id}/applications/{application_id}")
async def create_application(
    job_id: str,
    application_id: str,
    update_data: UpdateJobApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """
    Description
                Get endpoint for admin users to update a job application.

        Args:
                db: the database session object
        job_id: the ID of the Job

        Returns:
                Response: a response object containing details if successful or appropriate errors if not
        """

    check_model_existence(db, Job, job_id)
    check_model_existence(db, JobApplication, application_id)
    updated_application = job_application_service.update(
        db, application_id=application_id, job_id=job_id, schema=update_data)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Job Application updated successfully!",
        data=jsonable_encoder(updated_application)
    )

# Fetch all applications (superadmin)
@jobs.get("/{job_id}/applications", response_model=JobApplicationResponse, status_code=status.HTTP_200_OK,)
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

@jobs.delete('/{job_id}/applications/{application_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(job_id: str,
                             application_id: str,
                             db: Annotated[Session, Depends(get_db)],
                             current_user: Annotated[User, Depends(user_service.get_current_super_admin)]):
    """
    Deletes a single application.
    Args:
        job_id: The id of the job for the applicant
        application_id: The id of the application for the job
        db: database Session object
        current_user: the super admin user
    Returns:
        HTTP 204 No Content on success
    """
    job_application_service.delete(job_id, application_id, db)