from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from api.v1.models import User
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.services.user import user_service
from api.v1.services.session import session_service


session_router = APIRouter(prefix="/sessions", tags=["sessions"])

@session_router.get("/", response_model=success_response)
def get_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """
    Endpoint to get all sessions.

    args:
        - db: the database session
        - current_user: current authenticated user
    """
    sessions = session_service.fetch_all(db, current_user.id) 
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Sessions retrieved successfully",
        data=jsonable_encoder(sessions, exclude={"refresh_token"})
    )

@session_router.get('/{session_id}', response_model=success_response)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    session = session_service.fetch(db, current_user.id, session_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Session retrived successfully",
        data=jsonable_encoder(session, exclude={"refresh_token"})
    )

@session_router.delete('/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Endpoint to delete a session.

    args:
        - session_id (str): ID of the session
        - db: the database session
        - current_user: current authenticated user
    """
    return session_service.delete(db, current_user.id, session_id)

@session_router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    return session_service.delete_all(db, current_user.id)