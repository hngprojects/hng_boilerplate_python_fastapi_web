from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.v1.models.organization import Organization
from api.v1.schemas.organisations import OrganizationResponse

def get_organization_by_id(db: Session, org_id: int) -> OrganizationResponse:
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse.from_orm(organization)
