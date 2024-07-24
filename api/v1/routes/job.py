from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from api.v1.schemas.job import JobCreate, JobResponse
from api.v1.services.job import get_job_by_id, create_job
from api.db.database import get_db
from api.utils.dependencies import get_current_admin
from api.v1.models.user import User
from api.v1.models.job import Job

jobs = APIRouter(tags=["Jobs"])

# Endpoint to create a new job
@jobs.post("/jobs", response_model=JobResponse)
def create_new_job(job_data: JobCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_admin)):
    job = create_job(db, job_data, user_id)
    return job


# Endpoint to retrieve job details by ID
@jobs.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_current_admin)):
    job = get_job_by_id(db, job_id, user_id)
    return job
