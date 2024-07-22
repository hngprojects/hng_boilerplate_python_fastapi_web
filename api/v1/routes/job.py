# api/v1/routes/job.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.schemas.job import JobData, JobSchema, JobSuccessResponse

job = APIRouter(prefix="/jobs", tags=["Jobs"])


@job.get("/{job_id}", response_model=JobSuccessResponse)
async def get_job(job_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a job by its ID
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    res = JobSuccessResponse(
        statusCode=200,
        message="Job retrieval successful",
        data=JobData(
            id=job.id,
            user_id=job.user_id,
            title=job.title,
            description=job.description,
            location=job.location,
            salary=job.salary,
            job_type=job.job_type,
            company_name=job.company_name,
            created_at=job.created_at,
            updated_at=job.updated_at,
        ),
    )

    return res
