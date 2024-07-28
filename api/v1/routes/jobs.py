#!/usr/bin/env python3

from api.utils.success_response import success_response
from api.v1.schemas.jobs import PostJobSchema, AddJobSchema, JobCreateResponseSchema
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from fastapi import APIRouter, HTTPException, Depends
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.utils.logger import logger
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.jobs import job_service


jobs = APIRouter(prefix="/jobs", tags=["Jobs"])

@jobs.post("/", response_model=success_response,
           status_code=201,
           responses={422: {"descritption": "Invalid request data"},
                      401: {"description": "Unauthorized"},
                      500: {"description": "Server Error"}},
           )
async def add_jobs(
    job: PostJobSchema,
    db: Session = Depends(get_db),
    user: User = Depends(user_service.get_current_user)
):
    """
    Add a job listing to the database.
    This endpoint allows a user to post a job listing to the database.

    Parameters:
    - job: PostJobSchema
        The details of the job listing.
    - user: User (Depends on get_current_user)
        The current user posting the job request. This is a dependency that provides the user context.
    - db: The database session
    """
    if job.title.strip() == '' or job.description.strip() == '':
        raise HTTPException(status_code=400,
                            detail="Invalid request data"
                            )
    
    job_full = AddJobSchema(author_id=user.id, **job.model_dump())
    new_job = job_service.create(db, job_full)
    logger.info(f"Job Listing created successfully {new_job.id}")

    return success_response(
        message = "Job listing created successfully",
        status_code = 201,
        data = jsonable_encoder(JobCreateResponseSchema.model_validate(new_job))
        )