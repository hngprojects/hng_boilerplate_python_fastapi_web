from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services.user_organisations import user_organisations_service
from api.v1.services.user import get_current_user
from api.v1.models.user import User

router = APIRouter()

@router.get("/organizations/")
def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organizations = user_organisations_service.get_user_organizations(db=db, user=current_user)
    return {"status_code": 200, "message": "Organizations retrieved successfully", "data": [org.to_dict() for org in organizations]}
