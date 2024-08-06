"""Defines Teams Endpoints"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.session import Session
from starlette import status

from api.db.database import get_db
from api.utils.logger import logger
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.team import (PostTeamMemberSchema,
                                 TeamMemberCreateResponseSchema,
                                 UpdateTeamMember)
from api.v1.services.team import TeamServices, team_service
from api.v1.services.user import user_service

team = APIRouter(prefix="/team", tags=["Teams"])


@team.get(
    '/members/{team_id}',
    response_model=success_response,
    status_code=status.HTTP_200_OK
)
def get_team_member_by_id(
    team_id: Annotated[str, Path(description="Team Member ID")],
    db: Session = Depends(get_db),
    su: User = Depends(user_service.get_current_super_admin)
):
    '''Endpoint to fetch a team by id'''
    team_response = team_service.fetch(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return success_response(
        status_code=status.HTTP_200_OK,
        message='Team fetched successfully',
        data=jsonable_encoder(team_response),
    )


@team.patch(
    '/members/{team_id}',
    response_model=success_response,
    status_code=status.HTTP_200_OK
)
def update_team_member_by_id(
    team_id: Annotated[str, Path(description="Team Member ID")],
    team_data: UpdateTeamMember,
    db: Session = Depends(get_db),
    su: User = Depends(user_service.get_current_super_admin),
):
    '''Endpoint to update a team by id'''

    team_response = team_service.update(
        db, team_id, team_data.model_dump(exclude_unset=True,
                                          exclude_none=True))
    return success_response(
        status_code=status.HTTP_200_OK,
        message='Team updated successfully',
        data=jsonable_encoder(team_response),
    )


@team.post(
    "/members",
    response_model=success_response,
    status_code=201,

)
async def add_team_members(
    member: PostTeamMemberSchema,
    db: Session = Depends(get_db),
    admin: User = Depends(user_service.get_current_super_admin),
):
    """
    Add a team member to the database.
    This endpoint allows an admin add a new team member to the database.

    Parameters:
    - team: PostTeamMemberSchema
        The details of the team member.
    - admin: User (Depends on get_current_super_admin)
        The current admin adding the team member. This is a dependency that provides the admin context.
    - db: The database session
    """
    new_member = TeamServices.create(db, member)
    logger.info(f"Team Member added successfully {new_member.id}")

    return success_response(
        message="Team Member added successfully",
        status_code=201,
        data=jsonable_encoder(
            TeamMemberCreateResponseSchema.model_validate(new_member))
    )
