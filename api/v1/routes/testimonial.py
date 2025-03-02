#!/usr/bin/env python3
"""
Module contains CRUD routes for testimonial
"""
from fastapi.encoders import jsonable_encoder
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.v1.models.user import User
from fastapi import Depends, APIRouter, status,Query
from api.utils.success_response import success_response
from api.v1.services.testimonial import testimonial_service
from api.v1.services.user import user_service
from api.v1.schemas.testimonial import CreateTestimonial
from api.core.responses import SUCCESS
from typing import Annotated
from api.utils.pagination import paginated_response
from api.v1.models.testimonial import Testimonial
import json
import logging
from api.utils.logger import logger

testimonial = APIRouter(prefix="/testimonials", tags=['Testimonial'])

logger = logging.getLogger(__name__)


@testimonial.get("", status_code=status.HTTP_200_OK)
def get_testimonials(
    page_size: Annotated[int, Query(ge=1, description="Number of products per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 0,
    db: Session = Depends(get_db),
):
    """End point to Query Testimonials with pagination"""

    return paginated_response(
        db=db,
        model=Testimonial,
        limit=page_size,
        skip=max(page,0),
    )


@testimonial.get("/{testimonial_id}", status_code=status.HTTP_200_OK)
def get_testimonial(
    testimonial_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get testimonial by id"""

    testimonial = testimonial_service.fetch(db, testimonial_id)

    return success_response(
        status_code=200,
        message=f"Testimonial {testimonial_id} retrieved successfully",
        data=jsonable_encoder(testimonial),
    )


@testimonial.delete("/{testimonial_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testimonial(
    testimonial_id: str,
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Function for deleting a testimonial based on testimonial id
    """

    testimonial_service.delete(db, testimonial_id)


@testimonial.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_testimonials(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """
    Deletes all testimonials
    """

    testimonial_service.delete_all(db)

@testimonial.post('/', response_model=success_response)
def create_testimonial(
    testimonial_data: CreateTestimonial,
    db: Annotated[Session, Depends(get_db)],
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to create testimonial'''
    testimonial = testimonial_service.create(db, current_user, testimonial_data)
    response = success_response(
        status_code=201,
        message=SUCCESS,
        data={"id": testimonial.id}
    )
    return response

@testimonial.get("/user/{user_id}", status_code=status.HTTP_200_OK)
def get_user_testimonials(
    user_id: str,
    page_size: Annotated[int, Query(ge=1, description="Number of testimonials per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get all testimonials for a specific user with pagination"""
    try:
        # Only check if user is accessing their own testimonials
        if user_id != str(current_user.id):
            return {
                "status_code": 403,
                "message": "You can only view your own testimonials"
            }

        # Simply return the paginated response
        return paginated_response(
            db=db,
            model=Testimonial,
            limit=page_size,
            skip=max(page, 0),
            filters={"author_id": user_id}
        )
        
    except Exception as e:
        logger.exception(f"Error retrieving testimonials: {str(e)}")
        return {
            "status_code": 500,
            "message": "An unexpected error occurred"
        }
