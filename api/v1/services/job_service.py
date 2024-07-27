from sqlalchemy.orm import Session
from api.v1.models.job import Job
from api.v1.schemas.job import JobUpdate

class JobService:
    @staticmethod
    def get_job_by_id(db: Session, job_id: str) -> Job:
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def update_job(db: Session, db_job: Job, job_update: JobUpdate) -> Job:
        update_data = job_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
        return db_job
