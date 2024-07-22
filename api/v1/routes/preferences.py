from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from uuid import UUID
from api.v1.models.user import User
from api.v1.schemas import schemas
from api.utils import crud, deps
from api.utils import oauth2
from api.v1.models.preference import  OrgPreference



router = APIRouter()
# current_user: User = Depends(deps.get_current_user)

@router.post("/api/v1/{organization_id}/preference", response_model=schemas.PreferenceResponse)
def create_preference(
    organization_id: UUID,
    preference: schemas.PreferenceCreate,
    db: Session = Depends(deps.get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    organization = crud.get_organization(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not current_user.is_admin or organization_id not in [org.id for org in current_user.organizations]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.create_preference(db, preference, organization_id)

@router.get("/api/v1/{organization_id}/{preference_id}", response_model=schemas.PreferenceResponse)
def get_preference(
    preference_id: UUID,
    preference: schemas.PreferenceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_preference = crud.get_preference(db, preference_id, preference)
    if not db_preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return db_preference

@router.put("/api/v1/{organization_id}/{preference_id}", response_model=schemas.PreferenceResponse)
def update_preference(
    preference_id: UUID,
    preference: schemas.PreferenceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_preference = crud.update_preference(db, preference_id, preference)
    if not db_preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return db_preference

@router.delete("/api/v1/{organization_id}/{preference_id}", response_model=schemas.PreferenceResponse)
def delete_preference(
    preference_id: UUID,
    preference: schemas.PreferenceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    db_preference = db.query(OrgPreference).filter(OrgPreference.id == preference_id)
    if preference.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"preference with id:{preference_id} does not exist")
    
    preference.delete(sychronize_session=False)
    db.commit()
    return {"message": "preference succesfully deleted"}
