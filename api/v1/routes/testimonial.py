#!/usr/bin/env python3
"""
Testimonial CRUD routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from api.db.database import get_db
from api.v1.models.testimonial import Testimonial
from api.v1.models.user import User
from api.utils.dependencies import get_current_user, get_current_admin
from uuid import UUID

router = APIRouter(prefix="/testimonials", tags=["testimonials"])


@router.delete("/{testimonial_id}", response_model=dict)
def delete_testimonial(
    testimonial_id: UUID,
    # current_user: Annotated[User, Depends(get_current_user)],
    current_user: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    # retrieve the testimonial by ID
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()

    # check if a testimonial with the ID was retrieved or if it was not found
    # or if testimonial does not belong to user
    if (not testimonial) or (testimonial.user_id != current_user.id):
        raise HTTPException(
            detail="Testimonial not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # delete the testimonial
    db.delete(testimonial)
    db.commit()

    # return a success response
    return JSONResponse(
        content={
            "success": True,
            "message": "Testimonial deleted successfully",
            "status_code": 200,
        },
        status_code=status.HTTP_200_OK,
    )
