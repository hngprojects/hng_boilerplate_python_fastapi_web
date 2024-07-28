from sqlalchemy.orm import Session
from api.v1.models.org import Organization

def delete(db: Session, org_id: int) -> bool:
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    
    if organization:
        db.delete(organization)
        db.commit()
        return True
    else:
        return False
