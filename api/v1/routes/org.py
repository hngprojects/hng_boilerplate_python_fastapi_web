from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.db.database import get_db
from api.v1.services.user import user_service
from uuid_extensions import uuid7
from uuid import UUID
from ..schemas.org import OrganizationUsersResponse
from ..models.org import Organization
from ..models.user import User

org = APIRouter(prefix='/organizations', tags=['Organization'])




@org.get("/{org_id}/users", status_code=status.HTTP_200_OK)
async def get_organization_users(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user) 
):
    """Retrieve all users in an organisation"""
    # Check if the organization exists
    org = db.query(Organization).filter(Organization.id == str(org_id)).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Check if the current user has access to this organization
    user =  any(user.id == current_user.id for user in org.users)

    if not user:
        raise HTTPException(status_code=403, detail="You don't have access to this organization")

    # Fetch users from the database
    users = org.users

    # If no users found, raise an HTTPException
    if not users:
        return []

    # Create the response
    response = OrganizationUsersResponse(org_id=org_id, users=users)

    return {
        "status": "200",
        "message": "organization users retrieved successfully",
        "data": response.model_dump()
    }
