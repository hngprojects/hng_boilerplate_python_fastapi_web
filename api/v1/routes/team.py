#!/usr/bin/env python3

from api.utils.success_response import success_response
from api.v1.schemas.team import PostTeamMemberSchema, AddTeamSchema, TeamMemberCreateResponseSchema
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from fastapi import APIRouter, HTTPException, Depends
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from api.utils.logger import logger
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.team import TeamMemberService

teams = APIRouter(prefix="/team/members", tags=["Teams"])


@teams.post(
    "",
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
    if member.name.strip() == "" or member.role.strip() == "" or member.description.strip() == "" or member.picture_url.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid request data")
    

    new_member = TeamMemberService.create(db, member)
    logger.info(f"Team Member added successfully {new_member.id}")

    return success_response(
        message = "Team Member added successfully",
        status_code = 201,
        data = jsonable_encoder(TeamMemberCreateResponseSchema.model_validate(new_member))
    )