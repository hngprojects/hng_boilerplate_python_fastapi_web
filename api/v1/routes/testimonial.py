#!/usr/bin/env python3
"""
Testimonial route to create a testimonial
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from api.v1.schemas.testimonial import TestimonialCreate, TestimonialResponse, SuccessResponse
from api.db.database import get_db
from api.v1.models.testimonial import Testimonial
from api.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["testimonials"])

@router.post("/testimonials", response_model=SuccessResponse)
def create_testimonial(testimonial: TestimonialCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_testimonial = Testimonial( 
    	firstname=testimonial.firstname,
        lastname=testimonial.lastname,
        content=testimonial.content,
        user_id=current_user.id
    )
    db.add(db_testimonial)
    db.commit()
    db.refresh(db_testimonial)

    response_data = TestimonialResponse(
        id=db_testimonial.id,
        firstname=db_testimonial.firstname,
        lastname=db_testimonial.lastname,
        content=db_testimonial.content,
        created_at=db_testimonial.created_at,
        updated_at=db_testimonial.updated_at
    )

    return SuccessResponse(
        status="success",
        message="Testimonial created successfully",
        data=response_data
    )
