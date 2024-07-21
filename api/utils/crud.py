from sqlalchemy.orm import Session
from api.v1.models.org import Organization
from api.v1.models.preference import  OrgPreference
from api.v1.models.user import User
from api.v1.schemas.schemas import PreferenceCreate, PreferenceUpdate
from uuid import UUID
from api import db



def get_organization(db: Session, organization_id: UUID):
    return db.query(Organization).filter(Organization.id == organization_id).first()

def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

def create_preference(db: Session, preference: PreferenceCreate, organization_id: UUID):
    db_preference = OrgPreference(**preference.dict(), organization_id=organization_id)
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def get_preference(db: Session, preference_id: UUID, preference: PreferenceUpdate):
    db_preference = db.query(OrgPreference).filter(OrgPreference.id == preference_id).first()    
    return db_preference


def update_preference(db: Session, preference_id: UUID, preference: PreferenceUpdate):
    db_preference = db.query(OrgPreference).filter(OrgPreference.id == preference_id).first()
    if db_preference:
        for key, value in preference.dict().items():
            setattr(db_preference, key, value)
        db.commit()
        db.refresh(db_preference)
    return db_preference