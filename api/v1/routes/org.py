from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.org import Organization
# from api.v1.schemas.user import DeactivateUserSchema
from api.db.database import get_db
from api.utils.dependencies import get_current_user


org = APIRouter(prefix='/api/v1/organization', tags=['Organizations'])

@org.post("/{org_id}/add-user", status_code=200)

async def add_user_to_organization(
    request: Request,
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Fetch the organization by ID
       organization = db.query(Organization).filter(Organization.id == org_id).first()
       if organization is None:
           raise HTTPException(status_code=404, detail="Organization not found")

       # Fetch the user to be added
       user_to_add = db.query(User).filter(User.id == user.id).first()
       if user_to_add is None:
           raise HTTPException(status_code=404, detail="User not found")

       # Check if the user is already a member of the organization
       if user_to_add in organization.users:
           raise HTTPException(status_code=400, detail="User is already a member of the organization")

       # Add the user to the organization
       organization.users.append(user_to_add)

       # Commit the changes to the database
       db.commit()
       db.refresh(organization)

       return {
           "status": "success",
           "message": "User added to organisation successfully",
       }
