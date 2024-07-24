from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from api.v1.schemas.job import JobCreate, JobResponse
from api.v1.services.job import get_job_by_id
from api.db.database import get_db
from api.utils.dependencies import get_current_user
from api.v1.models.user import User
from api.v1.models.job import Job

jobs = APIRouter(prefix='/jobs', tags=["Jobs"])

# Endpoint to create a new job

# Endpoint to retrieve job details by ID
@jobs.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    job = get_job_by_id(db, job_id, current_user.id)
    return job
