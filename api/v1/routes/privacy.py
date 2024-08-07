from typing import Annotated, Optional
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.privacy_policies import (
    PrivacyPolicyCreate, PrivacyPolicyResponse, PrivacyPolicyUpdate
)
from api.db.database import get_db
from api.v1.services.privacy_policies import privacy_service
from api.v1.services.user import user_service


privacies = APIRouter(prefix="/privacy-policy", tags=["Privacy Policy"])


@privacies.post("", response_model=PrivacyPolicyResponse, status_code=status.HTTP_201_CREATED)
def create_privacy(privacy: PrivacyPolicyCreate, db: Session = Depends(get_db),
                  superadmin_user: User = Depends(user_service.get_current_super_admin)):
    privacy_item = privacy_service.create(db, privacy)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message='Privacy created successfully',
        data=jsonable_encoder(privacy_item)
    )


@privacies.get("", response_model=List[PrivacyPolicyResponse])
def get_privacies(db: Session = Depends(get_db)):
    """Get All Privacies"""
    privacy_items = privacy_service.fetch_all(db)
    
    return success_response(
        status_code=200,
        message='Privacies retrieved successfully',
        data=jsonable_encoder(privacy_items)
    )


@privacies.get("/{privacy_id}", response_model=PrivacyPolicyResponse)
def get_privacy(privacy_id: str, db: Session = Depends(get_db)):
    privacy = privacy_service.fetch(db, privacy_id)
    
    return success_response (
        status_code=200,
        message='privacy retrieved successfully',
        data=jsonable_encoder(privacy)
    )
    
@privacies.delete("/{privacy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_privacy(privacy_id: str, db: Session = Depends(get_db), superadmin_user: User = Depends(user_service.get_current_super_admin)):
    """Delete a Privacy Policy"""
    privacy_service.delete(db, privacy_id)


@privacies.patch("/{privacy_id}", response_model=PrivacyPolicyResponse)
def update_privacy(privacy_id: str, privacy: PrivacyPolicyUpdate, db: Session = Depends(get_db), superadmin_user: User = Depends(user_service.get_current_super_admin)):
    db_privacy = privacy_service.update(db, privacy_id, privacy)
    return success_response(
        status_code=200,
        message='Privacy updated successfully',
        data=jsonable_encoder(db_privacy)
    )
