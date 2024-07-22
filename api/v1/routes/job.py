from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.utils.json_response import JsonResponseDict
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.schemas.job import JobCreate, JobResponseSchema

job = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@job.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
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

    parsed_job = new_job.to_dict()
    parsed_job["user_id"] = str(parsed_job["user_id"])
    parsed_job["salary"] = str(parsed_job["salary"])

    return JsonResponseDict(
        message="Job created successfully",
        data={"job": parsed_job},
        status_code=status.HTTP_201_CREATED,
    )
