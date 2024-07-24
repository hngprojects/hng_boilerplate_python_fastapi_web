from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.notification import Notification as NotificationModel
from api.v1.models.user import User as UserModel
from api.utils.json_response import JsonResponseDict
from api.utils.dependencies import get_current_user
from api.v1.schemas.token import TokenData

router = APIRouter()

@router.get("/notifications/current-user", tags=["Notifications"])
async def get_user_notifications(
    user_id: int = Query(..., description="ID of the current user"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get notifications for the current user.

    **Parameters:**
    - `user_id`: The ID of the current user (int).

    **Responses:**
    - **200 OK:** List of notifications.
    - **401 Unauthorized:** Invalid or missing credentials.
    - **403 Forbidden:** Unauthorized access.
    - **404 Not Found:** No notifications found.

    **Dependencies:**
    - `current_user`: Extracts the authenticated user from the token.
    - `db`: Database session.
    """
    # Ensure the user ID matches the authenticated user
    if current_user.username != db.query(UserModel).filter(UserModel.id == user_id).first().username:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    notifications = db.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for the user")

    return JsonResponseDict(
        message="Notifications fetched successfully",
        status_code=200,
        data={"notifications": notifications}
    )
