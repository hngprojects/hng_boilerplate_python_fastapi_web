from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.v1.models.job import Job
from api.v1.schemas.job import JobCreate


# Function to create a job
def create_job(db: Session, job_data: JobCreate, user_id: str):
    job = Job(
        user_id=user_id,
        title=job_data.title,
        description=job_data.description,
        location=job_data.location,
        salary=job_data.salary,
        job_type=job_data.job_type,
        company_name=job_data.company_name,
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# Function to get job by ID
def get_job_by_id(db: Session, job_id: int, user_id: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    return job