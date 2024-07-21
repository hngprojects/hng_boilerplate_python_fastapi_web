from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.schemas.job import JobCreate, JobResponseSchema
from api.v1.schemas.job import JobUpdate, JobResponse
from fastapi import APIRouter, Depends, HTTPException, status


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

# update a job post

@job.patch(
    "/{id}",
    response_model=JobResponse,
    summary="Update job post",
    description="This endpoint allows a user to update an existing job post by providing updated job details."
)
async def update_job_post(
    id: str,
    current_user: Annotated[User, Depends(get_current_user)],  # Ensure user is authenticated
    job_update: JobUpdate,
    db: Session = Depends(get_db),
):
    db_job_post = db.query(Job).filter(Job.id == id).first()
    if not db_job_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job post not found")

    # Check if the current user is the owner of the job post or an admin
    if str(current_user.id) != str(db_job_post.user_id) and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this job post")

    for key, value in job_update.model_dump(exclude_unset=True).items():
        setattr(db_job_post, key, value)

    db.add(db_job_post)
    db.commit()
    db.refresh(db_job_post)

    return {
        "message": "Job details updated successfully",
        "data": db_job_post,
        "status_code": status.HTTP_200_OK
    }