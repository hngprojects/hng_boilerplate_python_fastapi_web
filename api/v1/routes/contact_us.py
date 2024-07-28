from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from typing import Annotated
from api.core.responses import SUCCESS
from api.utils.json_response import JsonResponseDict
from api.v1.services.contact_us import contact_service
from api.v1.schemas.contact_us import CreateContactUs
from api.v1.models import *

contact_us = APIRouter(tags=["Contact Us"])


# CREATE
@contact_us.post("/contact-us", response_model=JsonResponseDict.response)
async def create_contact_us(data: CreateContactUs, db: Annotated[Session, Depends(get_db)]):
    """Add a new contact us message."""
    new_contact_us_message = contact_service.create(db, data)
    response = JsonResponseDict(
        message=SUCCESS,
        data={"id": new_contact_us_message.id},
        status_code=status.HTTP_201_CREATED,
    )
    return response
