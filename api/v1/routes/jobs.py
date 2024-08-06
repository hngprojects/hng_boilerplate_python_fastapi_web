#!/usr/bin/env python3

from api.utils.success_response import success_response
from api.v1.schemas.jobs import PostJobSchema, AddJobSchema, JobCreateResponseSchema, UpdateJobSchema
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from fastapi import APIRouter, HTTPException, Depends, status
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.utils.logger import logger
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.job import Job
from api.v1.services.jobs import job_service
from api.v1.services.job_application import job_application_service
from api.utils.pagination import paginated_response
from api.v1.schemas.job_application import CreateJobApplication, UpdateJobApplication

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
        message = "Job listing created successfully",
        status_code = 201,
        data = jsonable_encoder(JobCreateResponseSchema.model_validate(new_job))
    )


@jobs.get("") 
async def fetch_all_jobs(
    db: Session = Depends(get_db),
    page_size: int = 10 ,
    page: int = 0 ,
):
    """
	Description
		Get endpoint for unauthenticated users to retrieve all jobs.

	Args:
		db: the database session object

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	
    return paginated_response(
        db=db,
        model=Job,
        limit=page_size,
        skip=max(page,0),
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

    job_application = job_application_service.create(db=db, schema=application, job_id=job_id)

    return success_response(
        status_code=201,
        message="Job application submitted successfully",
        data=jsonable_encoder(job_application)
    )
