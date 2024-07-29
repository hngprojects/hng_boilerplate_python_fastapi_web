from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.v1.models.job import Job
from api.v1.models.user import User
from api.v1.services.job import job_service
from api.db.database import get_db
from api.v1.services.user import user_service
from api.utils.success_response import success_response
from typing import Optional

router = APIRouter()

@router.put("/jobs/{job_id}", response_model=Job)
def update_job(
    job_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    department: Optional[str] = None,
    location: Optional[str] = None,
    salary: Optional[str] = None,
    job_type: Optional[str] = None,
    company_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    job_service.db = db
    updated_job = job_service.update_job(
        job_id=job_id,
        user=current_user,
        title=title,
        description=description,
        department=department,
        location=location,
        salary=salary,
        job_type=job_type,
        company_name=company_name,
    )

    return success_response(
        status_code = 200,
        message = "Updated Successfully",
        data = updated_job
    )
