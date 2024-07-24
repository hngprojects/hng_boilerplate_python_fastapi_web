from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.org import Organization
# from api.v1.schemas.user import DeactivateUserSchema
from api.db.database import get_db
from api.utils.dependencies import get_current_user
from api.v1.services.org import OrganizationService as organization_service


org = APIRouter(prefix='/organization', tags=['Organizations'])

@org.post("/{org_id}/add-user", status_code=200)
async def add_user_to_organization(
    request: Request,
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    organization_service.add_user(db=db, org_id=org_id, user=user)

    return {
        "status": "success",
        "message": "User added to organisation successfully",
    }
