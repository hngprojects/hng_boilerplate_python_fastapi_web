from typing import Any, Optional
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.job import Job
from fastapi import HTTPException


class JobService(Service):
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


    @staticmethod
    def fetch(db: Session, id: str) -> Optional[Job]:
        """Fetches a job by ID"""
        return db.query(Job).filter(Job.id == id).first()

    def fetch(self, db: Session, id: str):
        """Fetches a job by id"""
        job = db.query(Job).filter(Job.id == id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job


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
