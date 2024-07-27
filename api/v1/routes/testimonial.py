#!/usr/bin/env python3
"""
Module contains CRUD routes for testimonial
"""
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from fastapi import Depends, HTTPException, APIRouter, Request, Response, status, Security, Query
from fastapi.responses import JSONResponse
from api.utils.success_response import success_response
from api.utils.json_response import JsonResponseDict
from api.v1.services.testimonial import testimonial_service
from api.v1.services.user import user_service
from fastapi_pagination import Page, Params, paginate
from datetime import datetime
from api.v1.services.user import UserService

testimonial = APIRouter(prefix='/testimonials', tags=['Testimonial'])

@testimonial.delete("/{testimonial_id}")
def delete_testimonial(
    testimonial_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Function for deleting a testimonial based on testimonial id
    """
    if not testimonial_service.delete(db, testimonial_id):
        raise HTTPException(
            detail="Testimonial not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return JSONResponse(
        content={
            "success": True,
            "message": "Testimonial deleted successfully",
            "status_code": status.HTTP_200_OK
        },
        status_code=status.HTTP_200_OK
    )

@testimonial.get('/{testimonial_id}', status_code=status.HTTP_200_OK)
def get_testimonial(
    testimonial_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to get testimonial by id'''
    testimonial = testimonial_service.fetch(db, testimonial_id)
    if testimonial and testimonial_id == testimonial.id:
        return success_response(
            status_code=200,
            message=f'Testimonial {testimonial_id} retrieved successfully',
            data={
                'id': testimonial.id,
                'client_designation': testimonial.client_designation,
                'client_name': testimonial.client_name,
                'author_id': testimonial.author_id,
                'comments': testimonial.comments,
                'content': testimonial.content,
                'ratings': testimonial.ratings, 
            }
        )
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "status_code": 404,
            "message": f'Testimonial {testimonial_id} not found'
        }
    )

@testimonial.delete("/", response_class=JsonResponseDict)
async def delete_all_testimonials(db: Session = Depends(get_db)):
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
