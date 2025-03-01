from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timezone

from api.utils.settings import settings

celery_app = Celery('api', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

celery_app.conf.beat_schedule = {
    "clean_db_every_day": {
        "task": "api.utils.celery_config.clean_expired_and_revoked_tokens_from_sessions_table",
        "schedule": crontab(day_of_week=0, hour=0, minute=0)# run every sunday midnight 
    }
}

celery_app.conf.timezone = "UTC"

@celery_app.task
def clean_expired_and_revoked_tokens_from_sessions_table():
    """Clean expired and revoked tokens from the sessions table."""
    from api.db.database import get_db
    from api.v1.models.session import UserSession
    from sqlalchemy import cast, DateTime
    
    db = next(get_db())
    try:
        current_time = datetime.now(timezone.utc)
        db.query(UserSession).filter(UserSession.is_revoked == True).delete()
        db.query(UserSession).filter(cast(UserSession.expires_at, DateTime) < current_time).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
