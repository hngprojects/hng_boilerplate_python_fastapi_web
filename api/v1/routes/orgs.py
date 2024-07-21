from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from api.v1.schemas.role import RoleCreate, ResponseModel
from api.db.database import get_db
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from api.utils.dependencies import get_current_admin, get_current_user
from api.v1.schemas.orgs import OrganizationCreate, OrganizationResponse

org = APIRouter(prefix="/organizations", tags=["Organizations"])


@org.post("/", response_model=OrganizationResponse)
def create_organization(
    current_user: Annotated[User, Depends(get_current_user)],
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
):
    db_org = Organization(
        name=organization.name,
        description=organization.description
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return OrganizationResponse(id=db_org.id,
                                name=db_org.name,
                                description=db_org.description,
                                status_code=201,
                                message="Organization created succesfully")
