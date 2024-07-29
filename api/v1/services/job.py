from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.db.database import get_db
from api.v1.models.job import Job
from api.v1.models.user import User
from typing import Optional

class JobService(Service):

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    def check_author(self, job: Job, user: User):
        if job.author_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to update this job")

    def update_job(self,
                   job_id: str,
                   user: User,
                   title: Optional[str] = None,
                   description: Optional[str] = None,
                   department: Optional[str] = None,
                   location: Optional[str] = None,
                   salary: Optional[str] = None,
                   job_type: Optional[str] = None,
                   company_name: Optional[str] = None,
            ) -> Job:

        job = self.get_job_by_id(job_id)
        self.check_author(job, user)

        if title:
            job.title = title
        if description:
            job.description = description
        if department:
            job.department = department
        if location:
            job.location = location
        if salary:
            job.salary = salary
        if job_type:
            job.job_type = job_type
        if company_name:
            job.company_name = company_name

        self.db.commit()
        self.db.refresh(job)
        return job

job_service = JobService()

