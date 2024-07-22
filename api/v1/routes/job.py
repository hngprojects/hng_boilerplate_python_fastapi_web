from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.schemas.job import JobUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from utils.json_response import JsonResponseDict


job = APIRouter(
    prefix="/api/v1/jobs",
    tags=["todos"],
)


# update a job post

@job.patch(
    "/jobs/{id}",
    response_model=JsonResponseDict,
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