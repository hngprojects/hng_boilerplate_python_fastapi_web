from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.v1.schemas import region_schemas
from api.v1.models.region import Region
from api.db.database import get_db
from api.utils.dependencies import get_current_user, get_current_admin

region = APIRouter(prefix="/regions",tags=["Regions"])

# Region Add Endpoint
@region.post(
    "/", response_model=region_schemas.RegionBase, status_code=status.HTTP_201_CREATED
)
def create_region(
    region: region_schemas.RegionBase, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_admin)
):
    db_region = db.query(Region).filter(Region.region_code == region.region_code).first()
    if db_region:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {"field": "region_code", "message": "Region code already registered"}
            ],
        )
    try:
        # Add created_by field to the new Region instance
        new_region = Region(
            **region.dict(), 
            created_by=current_user['id']  # Automatically set created_by
        )
        db.add(new_region)
        db.commit()
        db.refresh(new_region)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred: " + str(e),
        )
    return new_region



# Region List Endpoint
@region.get(
    "/",
    response_model=List[region_schemas.RegionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_regions(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    regions = db.query(Region).all()
    return regions
