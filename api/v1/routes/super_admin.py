from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
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
from api.v1.models.super_admin import SuperAdmin
from api.v1.schemas.super_admin import SuperCreate


super_admin = APIRouter(prefix="/super_admin", tags=["Super_Admin"])

@super_admin.post("/", status_code=status.HTTP_201_CREATED)
def create_super_admin(curent_user: Annotated[User, Depends(get_current_user)], name: SuperCreate, db: Session = Depends(get_db)):
    super_admin_user = db.query(SuperAdmin).filter_by(name=name).first()
    if super_admin_user:
        raise HTTPException(status_code=400, detail="Super Admin Already Exist")
    super_admin_user = SuperAdmin(name)
    db.add(super_admin_user)
    db.commit()
    db.refresh(super_admin_user)
    return super_admin_user