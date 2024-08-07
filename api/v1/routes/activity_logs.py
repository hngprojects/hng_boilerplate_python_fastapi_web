from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.schemas.activity_logs import ActivityLogCreate, ActivityLogResponse
from api.v1.services.activity_logs import activity_log_service
from api.v1.services.user import user_service
from api.db.database import get_db
from api.utils.success_response import success_response

activity_logs = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])


@activity_logs.post("/create", status_code=status.HTTP_201_CREATED)
async def create_activity_log(
    activity_log: ActivityLogCreate, db: Session = Depends(get_db)
):
    """Create a new activity log"""

    new_activity_log = activity_log_service.create_activity_log(
        db=db,
        user_id=activity_log.user_id,
        action=activity_log.action
    )

    return success_response(
        status_code=201,
        message="Activity log created successfully",
        data=jsonable_encoder(new_activity_log)
    )


@activity_logs.get("", response_model=list[ActivityLogResponse])
async def get_all_activity_logs(current_user: User = Depends(user_service.get_current_super_admin), db: Session = Depends(get_db)):
    '''Get all activity logs'''

    activity_logs = activity_log_service.fetch_all(db=db)

    return success_response(
        status_code=200,
        message="Activity logs retrieved successfully",
        data=jsonable_encoder(activity_logs)
    )

@activity_logs.get("/{user_id}", status_code=status.HTTP_200_OK)
async def fetch_all_users_activity_log(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
):
    """
    Get endpoint for admin users get a users activity logs.

    Args:
        user_id (str): the id of user
        current_user: the admin user
        db: the database session object

    Returns:
        Response: a response object containing details if successful or appropriate errors if not
    """


    activity_logs = activity_log_service.fetch_all(
        db=db,
        user_id=user_id
    )

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Activity logs fetched successfully!",
        data=jsonable_encoder(activity_logs)
    )

@activity_logs.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
):
    """Endpoint to delete an activity log by its ID"""
    
    activity_log_service.delete_activity_log_by_id(db, log_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message=f"Activity log with ID {log_id} deleted successfully"
    )
