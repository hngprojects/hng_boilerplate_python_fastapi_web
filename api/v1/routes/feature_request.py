from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.schemas.feature_request import (
    FeatureRequestCreate,
    FeatureRequestResponse,
    FeatureRequestUpdate
)
from api.v1.services.feature_request import FeatureRequestService
from api.v1.services.user import user_service
from api.v1.models.user import User

feature_request = APIRouter(prefix="/feature-request", tags=["Feature Requests"])


@feature_request.post("/", response_model=FeatureRequestResponse, status_code=status.HTTP_201_CREATED)
def create_feature_request(
    feature_request_data: FeatureRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Create a new feature request
    """
    return FeatureRequestService.create_feature_request(db, feature_request_data, current_user.id)


@feature_request.get("/", response_model=List[FeatureRequestResponse])
def get_feature_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Get all feature requests
    """
    # If user is a superadmin, return all feature requests
    if current_user.is_superadmin:
        return FeatureRequestService.get_feature_requests(db, skip, limit)
    # Otherwise, return only the user's feature requests
    return FeatureRequestService.get_user_feature_requests(db, current_user.id, skip, limit)


@feature_request.get("/{feature_request_id}", response_model=FeatureRequestResponse)
def get_feature_request(
    feature_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Get a feature request by ID
    """
    feature_request = FeatureRequestService.get_feature_request_by_id(db, feature_request_id)
    if not feature_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )
    
    # Check if the user is allowed to access this feature request
    if not current_user.is_superadmin and feature_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this feature request"
        )
    
    return feature_request


@feature_request.put("/{feature_request_id}", response_model=FeatureRequestResponse)
def update_feature_request(
    feature_request_id: str,
    feature_request_update: FeatureRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Update a feature request
    """
    existing_feature_request = FeatureRequestService.get_feature_request_by_id(db, feature_request_id)
    if not existing_feature_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )
    
    # Check if the user is allowed to update this feature request
    if not current_user.is_superadmin and existing_feature_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this feature request"
        )

     # Prevent non-superadmins from updating the status field
    update_data = feature_request_update.dict(exclude_unset=True)
    if not current_user.is_superadmin and "status" in update_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update the status field"
        )
        
    updated_feature_request = FeatureRequestService.update_feature_request(
        db, feature_request_id, feature_request_update
    )
    return updated_feature_request


@feature_request.delete("/{feature_request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature_request(
    feature_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Delete a feature request
    """
    existing_feature_request = FeatureRequestService.get_feature_request_by_id(db, feature_request_id)
    if not existing_feature_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature request not found"
        )
    
    # Check if the user is allowed to delete this feature request
    if not current_user.is_superadmin and existing_feature_request.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this feature request"
        )
    
    FeatureRequestService.delete_feature_request(db, feature_request_id)
    return None
