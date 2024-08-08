from fastapi import status, Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2
from datetime import datetime, timedelta
from api.db.database import get_db
from api.v1.services.user import oauth2_scheme
from api.v1.services.analytics import analytics_service, AnalyticsServices

statistics = APIRouter(prefix='/statistics')


def get_current_month_date_range():
    now = datetime.utcnow()
    start_date = datetime(now.year, now.month, 1)
    end_date = (start_date + timedelta(days=32)
                ).replace(day=1) - timedelta(seconds=1)
    return start_date, end_date





@statistics.get('', status_code=status.HTTP_200_OK)
async def get_analytics_summary(
   token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
    analytics_service: Annotated[AnalyticsServices, Depends()],
    start_date: datetime = None,
    end_date: datetime = None
):
    
    """
    Retrieves analytics summary data for an organization or super admin.
    Args:
        token: access_token
        db: database Session object
        start_date: start date for filtering
        end_date: end date for filtering
    Returns:
        analytics response: contains the analytics summary data
    """
    if not start_date or not end_date:
        start_date, end_date = get_current_month_date_range()
    return analytics_service.get_analytics_summary(token=token, db=db, start_date=start_date, end_date=end_date)
