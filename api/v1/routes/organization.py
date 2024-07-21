#!/usr/bin/python3
"""
Contains routes for organisation creation
"""
from api.v1.models.org import Organization
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.schemas.organization_schemas import Org_request, Response, Data
from api.v1.services.auth_utils import get_current_user
from api.v1.models.user import User

app = APIRouter(prefix="/api/v1")


@app.post(
        "/organisations",
        response_model=Response,
        status_code=status.HTTP_201_CREATED
        )
def create_organization(
    data: Org_request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates an Organisation object and adds it to db
    """
    new_org = Organization(**data.dict(), owner_id=user.id)
    db.add(new_org)
    db.commit()
    slug = f"{new_org.name.replace(' ', '-')}-{str(new_org.id).split('-')[-1]}"
    new_org.slug = slug
    db.commit()
    db.refresh(new_org)
    org_data = Data(
        id=str(new_org.id),
        name=new_org.name,
        description=new_org.description,
        owner_id=str(new_org.owner_id),
        slug=new_org.slug,
        email=new_org.email,
        industry=new_org.industry,
        type=new_org.type,
        country=new_org.country,
        address=new_org.address,
        state=new_org.state,
        created_at=new_org.created_at,
        updated_at=new_org.updated_at
        )
    return Response(data=org_data)
