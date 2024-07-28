from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from api.v1.models import Job
from ..schemas.job_update import JobUpdateSchema
from api.db.database import get_db 
from api.utils.dependencies import get_current_user

app = FastAPI()

@app.put("/jobs/{job_id}", response_model=Job)
async def update_job(
    job_id: str,
    job_update: JobUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.author_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this job")

    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    
    return {
        "success": True,
        "status_code": 200,
        "message": "Job updated successfully",
        "data": job
    }
