# api/v1/routes/job.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.job import JobUpdate
from api.v1.services.job_service import JobService
from api.v1.routes.job import job

job = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

async def update_job_post(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    job_update: JobUpdate,
    db: Session = Depends(get_db),
):
    db_job_post = JobService.get_job_by_id(db, job_id)
    if not db_job_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job post not found")

    # Check if the current user is the owner of the job post or an admin
    if str(current_user.id) != str(db_job_post.user_id) and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this job post")

    # Use the service to update the job post
    updated_job = JobService.update_job(db, db_job_post, job_update)

    return {
        "message": "Job details updated successfully",
        "data": updated_job,
        "status_code": status.HTTP_200_OK
    }
