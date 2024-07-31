#!/usr/bin/env python3
"""
Module contains CRUD routes for testimonial
"""
from fastapi.encoders import jsonable_encoder
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from fastapi import Depends, HTTPException, APIRouter, Request, Response, status, Security, Query
from fastapi.responses import JSONResponse
from api.utils.success_response import success_response
from api.v1.services.testimonial import testimonial_service
from api.v1.services.user import user_service
from fastapi_pagination import Page, Params, paginate
from datetime import datetime
from api.v1.services.user import UserService
from api.v1.schemas.testimonial import CreateTestimonial
from api.core.responses import SUCCESS
from typing import Annotated
from api.utils.pagination import paginated_response
from api.v1.models.testimonial import Testimonial
from api.utils.json_response import JsonResponseDict

testimonial = APIRouter(prefix="/testimonials", tags=['Testimonial'])


@testimonial.get('', status_code=status.HTTP_200_OK)
def get_testimonials(
    page_size: int ,
    page: int,
    db: Session = Depends(get_db),
):
    """End point to Query Testimonials with pagination"""

    return paginated_response(
        db=db,
        model=Testimonial,
        limit=page_size,
        skip=max((page - 1),2) * page_size,
    )


@testimonial.get('/{testimonial_id}', status_code=status.HTTP_200_OK)
def get_testimonial(
    testimonial_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to get testimonial by id'''

    testimonial = testimonial_service.fetch(db, testimonial_id)

    return success_response(
        status_code=200,
        message=f'Testimonial {testimonial_id} retrieved successfully',
        data=jsonable_encoder(testimonial)
    )


@testimonial.delete("/{testimonial_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testimonial(
    testimonial_id: str,
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db)
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
    try:
        testimonial_service.delete_all(db)
        return JsonResponseDict(
            message="All testimonials deleted successfully",
            data={},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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


@testimonial.get("/")
async def get_testimonials(
    db: Session = Depends(get_db),
    params: Params = Depends(),
    current_user: User = Security(UserService().get_current_user),
    ratings: int = Query(None, ge=1, le=5, description="Rating of the testimonial (1-5)"),
    created_at: str = Query(None, description="Date of the testimonial in YYYY-MM-DD format")
):
    if ratings is not None and (ratings < 1 or ratings > 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    if created_at:
        try:
            datetime.strptime(created_at, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")

    query = db.query(Testimonial)

    if ratings:
        query = query.filter(Testimonial.ratings == ratings)
    
    if created_at:
        query = query.filter(Testimonial.created_at == created_at)

    return paginate(query, params)