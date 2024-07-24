from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.job import JobCreate, Job
from crud.job import create_job
from dependencies import get_db, get_current_admin_user

router = APIRouter()

@router.post("/create", response_model=Job)
def create_job_route(
    job: JobCreate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_admin_user)
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    return create_job(db=db, job=job)
