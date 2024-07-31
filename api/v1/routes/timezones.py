from typing import Annotated, Optional
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.regions import (
    LanguageCreate, LanguageOut, LanguageUpdate,
    RegionCreate, RegionOut, RegionUpdate,
    TimezoneCreate, TimezoneOut, TimezoneUpdate
)
from api.db.database import get_db
from api.v1.services.languages import lang_service
from api.v1.services.timezones import timezone_service

timezones = APIRouter(prefix="/timezones", tags=["Timezones"])


@timezones.post("", response_model=TimezoneOut, status_code=status.HTTP_201_CREATED)
def create_timezone(region: TimezoneCreate, db: Session = Depends(get_db)):
    region = timezone_service.create(db, TimezoneCreate)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message='Region created successfully',
        data=jsonable_encoder(region)
    )

@timezones.get("", response_model=List[RegionOut])
def get_regions(db: Session = Depends(get_db)):
    """Get All Regions"""
    regions = timezone_service.fetch_all(db)
    
    return success_response(
        status_code=200,
        message='Regions retrieved successfully',
        data=jsonable_encoder(regions)
    )

@timezones.get("/{user_id}", response_model=RegionOut)
def get_region_by_user(user_id: str, db: Session = Depends(get_db)):
    region = timezone_service.fetch(db, user_id)
    
    return success_response(
        status_code=200,
        message='Region retrieved successfully',
        data=jsonable_encoder(region)
    )

@timezones.put("/{user_id}", response_model=RegionOut)
def update_region(user_id: str, region: RegionUpdate, db: Session = Depends(get_db)):
    db_region = timezone_service.update(db, user_id, RegionUpdate)
    return success_response(
        status_code=200,
        message='Region updated successfully',
        data=jsonable_encoder(db_region)
    )

@timezones.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(user_id: str, db: Session = Depends(get_db)):
    region = timezone_service.delete(db, user_id)
    return