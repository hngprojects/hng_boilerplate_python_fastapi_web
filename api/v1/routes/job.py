from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.schemas.job import JobCreate, JobResponseSchema

job = APIRouter(
    prefix="/api/v1/jobs",
    tags=["todos"],
)


@job.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, int | str | JobResponseSchema],
    summary="Create job",
    description="This endpoint allows a user to create a new job by providing the necessary job details such as title, description, and requirements.",
)
async def create_job(
    job: JobCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    new_job = Job(**job.model_dump(), user_id=current_user.id)

    # save new job

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "status": status.HTTP_201_CREATED,
        "message": "Job listing created successfully",
        "data": new_job,
    }


# @job.get(
#     "",
#     response_model=dict[str, int | str | list[JobResponseSchema]],
#     status_code=status.HTTP_200_OK,
#     summary="Get all jobs",
#     description="This endpoint allows anyone to get all job listings.",
# )
# async def get_all_jobs(
#     db: Session = Depends(get_db),
# ):
#     jobs = db.query(Job).all()
#     return {
#         "status": status.HTTP_200_OK,
#         "message": "Job listings retrieved successfully",
#         "data": jobs,   
#     }

@job.get(
    "",
    response_model=dict[str, int | str | list[JobResponseSchema]],
    status_code=status.HTTP_200_OK,
    summary="Get all jobs",
    description="This endpoint allows anyone to get all job listings with pagination.",
)
async def get_all_jobs(
    db: Session = Depends(get_db),
    limit: int = Query(10, le=100, description="Number of job listings to return"),
    offset: int = Query(0, ge=0, description="Offset from which to start returning job listings")
):
    jobs_query = db.query(Job).offset(offset).limit(limit)
    jobs = jobs_query.all()
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Job listings retrieved successfully",
        "data": jobs,
    }
    



