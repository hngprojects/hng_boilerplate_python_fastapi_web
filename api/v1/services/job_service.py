from sqlalchemy.orm import Session
from api.v1.models.job import Job
from api.v1.schemas.job import JobUpdate

class JobService:
    @staticmethod
    def get_job_by_id(db: Session, job_id: str) -> Job:
        """
        Retrieve a job post by its ID.

        :param db: Database session
        :param job_id: ID of the job post
        :return: Job instance or None if not found
        """
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def update_job(db: Session, db_job: Job, job_update: JobUpdate) -> Job:
        """
        Update an existing job post with new data.

        :param db: Database session
        :param db_job: The existing job post to update
        :param job_update: The new data for the job post
        :return: The updated Job instance
        """
        update_data = job_update.job_type(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
        return db_job
