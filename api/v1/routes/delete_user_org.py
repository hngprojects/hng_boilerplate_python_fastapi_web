from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from api.v1.schemas.role import RoleCreate, ResponseModel
from api.db.database import get_db
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile

from api.v1.models.base import Base

from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from api.utils.dependencies import get_current_admin
from sqlalchemy.orm import Session
from api.v1.schemas.delete_userschema import  UserDelete



organization = APIRouter(prefix="/organizations", tags=["Organizations"])

@organization.delete("/organizations/{organization_id}/users/{user_id}",response_model=ResponseModel, status_code=204)
def delete_user_org(org_id: UserDelete, user_id: UserDelete, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):

    db_organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not db_organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if db_user.organization_id != org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not belong to the specified organization")
    
    db.delete(db_user)
    db.commit()

    return ResponseModel(message="User deleted successfully", status_code=200)



    