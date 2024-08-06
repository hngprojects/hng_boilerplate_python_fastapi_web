"""Defines Teams Endpoints"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.session import Session
from starlette import status

from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.team import team_service

team = APIRouter(prefix="/teams", tags=["Teams"])


@team.get(
    '/members/{team_id}',
    response_model=success_response,
    status_code=status.HTTP_200_OK
)
def get_team_member_by_id(
    team_id: Annotated[str, Path(description="Team Member ID")],
    db: Session = Depends(get_db),
    su: User = Depends(get_super_admin)
):
    '''Endpoint to fetch a team by id'''
    team = team_service.fetch(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return success_response(
        status_code=status.HTTP_200_OK,
        message='Team fetched successfully',
        data=jsonable_encoder(team),
    )
