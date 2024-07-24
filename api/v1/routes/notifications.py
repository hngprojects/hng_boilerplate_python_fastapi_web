from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api.v1.models.user import User
from api.v1.services.notification import notification_service
from api.v1.services.user import user_service

from api.db.database import get_db


notifications = APIRouter(prefix="/notifications", tags=["notifications"])


@notifications.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
    ):

    notification_service.delete(
        notification_id,
        user=current_user,
        db=db
        )
