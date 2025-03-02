from typing import Any, Optional
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.job import Job
from fastapi import HTTPException
from api.utils.db_validators import check_model_existence


class JobService():
    """Job service functionality"""

    def create(self, db: Session, schema) -> Job:
        """Create a new job"""

        new_job = Job(**schema.model_dump())
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        return new_job

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all jobs with option to search using query parameters"""

        query = db.query(Job)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Job, column) and value:
                    query = query.filter(getattr(Job, column).ilike(f"%{value}%"))

        return query.all()

    def retrieve(self, db: Session, job_id):
        """Fetches a job by ID"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job


    def fetch_by_filters(self, db: Session, title: str = None, location: str = None, job_type: str = None):
        """Fetch jobs by the specified filters"""
        query = db.query(Job)

        if title:
            query = query.filter(Job.title.ilike(f"%{title}%"))
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if job_type:
            query = query.filter(Job.job_type == job_type)

        jobs = query.all()

        if not jobs:
            raise HTTPException(
                status_code=404,
                detail="No jobs found matching the search parameters."
            )
        return jobs


    def update(self, db: Session, id: str, schema):
        """Updates a job"""

        job = self.fetch(db=db, id=id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(job, key, value)

        db.commit()
        db.refresh(job)
        return job

    def delete(self, db: Session, id: str):
        """Deletes a job"""

        job = self.fetch(db=db, id=id)
        db.delete(job)
        db.commit()


job_service = JobService()
