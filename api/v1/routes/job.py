from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.schemas.job import JobCreate, JobResponseSchema

job = APIRouter(prefix="/jobs", tags=["jobs"])


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
