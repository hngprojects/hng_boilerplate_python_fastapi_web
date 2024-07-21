# api/v1/routes/members.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import DataError
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.base import user_organization_association
from api.v1.schemas.membersSchemas import JsonResponseDict
from uuid import UUID
from enum import Enum
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

def validate_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False

class MemberStatus(str, Enum):
    all = "all"
    members = "members"
    suspended = "suspended"
    left = "left"

@router.get(
    "/organizations/{organization_id}/members",
    response_model=JsonResponseDict,
    tags=["Organization"],
    summary="Filter members of a specific organization based on status",
)
async def get_members(
    organization_id: str,
    status: MemberStatus = MemberStatus.all,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if not validate_uuid(organization_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format for organization id"
        )

    organization = db.query(Organization).filter(Organization.id == UUID(organization_id)).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    filters = [user_organization_association.c.organization_id == UUID(organization_id)]
    logger.debug(f"Initial filters: {filters}")

    if status != MemberStatus.all:
        filters.append(user_organization_association.c.status == status.value)
        logger.debug(f"Applied status filter: {status.value}")

    logger.debug(f"Querying members with page={page} and limit={limit}")

    try:
        query = db.query(
            User.id.label("user_id"),
            user_organization_association.c.organization_id,
            User.email.label("user_email"),
            Organization.name.label("organization_name")
        ).select_from(
            User
        ).join(
            user_organization_association
        ).join(
            Organization,
            Organization.id == user_organization_association.c.organization_id
        ).filter(and_(*filters)).offset((page - 1) * limit).limit(limit)

        logger.debug(f"SQL Query: {str(query.statement.compile(dialect=db.bind.dialect))}")

        members = query.all()
        logger.debug(f"Members retrieved: {members}")

        total_members = db.query(User.id).join(
            user_organization_association
        ).filter(and_(*filters)).count()
        logger.debug(f"Total members count: {total_members}")

    except DataError as e:
        logger.error("Data error during database query", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Invalid data or UUID format"
        )
    except Exception as e:
        logger.error("Error fetching members", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    if not members:
        raise HTTPException(
            status_code=404,
            detail="No members found"
        )

    prev_page = f"/api/v1/organizations/{organization_id}/members?status={status.value}&page={page - 1}&limit={limit}" if page > 1 else None
    next_page = f"/api/v1/organizations/{organization_id}/members?status={status.value}&page={page + 1}&limit={limit}" if len(members) == limit else None

    return JsonResponseDict(
        total=total_members,
        page=page,
        limit=limit,
        prev=prev_page,
        next=next_page,
        users=[
            {
                "user_id": str(member.user_id),
                "organization_id": str(member.organization_id),
                "user_email": member.user_email,
                "organization_name": member.organization_name
            }
            for member in members
        ]
    )
