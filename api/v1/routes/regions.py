from typing import Annotated, Optional
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.regions import (
    RegionCreate, RegionOut, RegionUpdate
)
from api.db.database import get_db
from api.v1.services.regions import region_service
from api.v1.services.user import user_service


regions = APIRouter(prefix="/regions", tags=["Regions, Timezone and Language"])

# Region Endpoints
@regions.post("", response_model=RegionOut, status_code=status.HTTP_201_CREATED)
def create_region(region: RegionCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(user_service.get_current_user)):
    region = region_service.create(db, region, current_user.id)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message='Region created successfully',
        data=jsonable_encoder(region)
    )

@regions.get("", response_model=List[RegionOut])
def get_regions_or_timezones(
    db: Session = Depends(get_db),
    timezones: Optional[bool] = Query(False, description="Set to true to fetch unique time zones")
):
    """
    Fetch all regions or unique time zones based on the timezones query parameter.
    """
    if timezones:
        unique_timezones = region_service.fetch_unique_timezones(db)
        if not unique_timezones:
            raise HTTPException(
                status_code=404,
                detail="No time zones found."
            )
        return success_response(
            status_code=200,
            message='Time zones retrieved successfully',
            data=unique_timezones
        )
    else:
        regions = region_service.fetch_all(db)
        return success_response(
            status_code=200,
            message='Regions retrieved successfully',
            data=regions
        )


@regions.get("/{region_id}", response_model=RegionOut)
def get_region_by_user(region_id: str, db: Session = Depends(get_db)):
    region = region_service.fetch(db, region_id)
    
    return success_response (
        status_code=200,
        message='Region retrieved successfully',
        data=jsonable_encoder(region)
    )

@regions.put("/{region_id}", response_model=RegionOut)
def update_region(region_id: str, region: RegionUpdate, db: Session = Depends(get_db)):
    db_region = region_service.update(db, region_id, region)
    return success_response(
        status_code=200,
        message='Region updated successfully',
        data=jsonable_encoder(db_region)
    )

@regions.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(region_id: str, db: Session = Depends(get_db)):
    region = region_service.delete(db, region_id)
    return
