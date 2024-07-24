from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.v1.models.job import Job
from api.v1.schemas.job import JobCreate


# Function to get job by ID
def get_job_by_id(db: Session, job_id: str, user_id: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    return job