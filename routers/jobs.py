from fastapi import APIRouter, HTTPException
from models import JobCreate

router = APIRouter()

jobs = []

@router.post("/api/v1/jobs/create", status_code=201)
def create_job(job: JobCreate):
    job_dict = job.dict()
    job_dict['id'] = len(jobs) + 1
    jobs.append(job_dict)
    return job_dict
