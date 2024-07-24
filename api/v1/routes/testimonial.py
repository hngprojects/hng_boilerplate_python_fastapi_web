#!/usr/bin/env python3
"""
Module contains CRUD routes for testimonial
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.utils.dependencies import get_current_admin
from api.v1.models.user import User
from api.v1.models.testimonial import Testimonial
from uuid import UUID

testmonial_route = APIRouter(tags=["testimonials"])

@testmonial_route.delete("/testimonials/{testimonial_id}")
def delete_testimonial(
    testimonial_id: UUID,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Function for deleting a testimonial based on testimonial id
    """
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not testimonial:
        raise HTTPException(
            detail="Testimonial not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    db.delete(testimonial)
    db.commit()
    return JSONResponse(
        content={
            "success": True,
            "message": "Testimonial deleted successfully",
            "status_code": status.HTTP_200_OK
        },
        status_code=status.HTTP_200_OK
    )
