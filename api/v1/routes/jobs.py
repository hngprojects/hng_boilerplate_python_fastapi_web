#!/usr/bin/env python3

from api.utils.success_response import success_response
from api.v1.schemas.jobs import PostJobSchema, AddJobSchema, JobCreateResponseSchema
from fastapi.exceptions import HTTPException

from fastapi import APIRouter, HTTPException, Depends
from api.utils.dependencies import get_current_user
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
    user: User = Depends(get_current_user)
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
    Returns:
    - 201: User added successfully
    - 401: Unauthorized
    """
    try:
        job_full = AddJobSchema(author_id=user.id, **job.model_dump())
        new_job = job_service.create(job_full)
        logger.info(f"Job Listing posted successfully {new_job.title}")

    except Exception as e:
        logger.error(f"Failed to post Job: {e.detail}")
        raise HTTPException(
            status_code=500, detail={"message": "Failed to post job",
                                     "status_code": 500})


    return success_response(
        message = "User added to waitlist successfully",
        status_code = 201,
        data = JobCreateResponseSchema.model_validate(new_job).model_dump(),
    )