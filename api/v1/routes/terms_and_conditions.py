from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.services.terms_and_conditions import terms_and_conditions_service
from api.v1.schemas.terms_and_conditions import UpdateTermsAndConditions
from api.v1.services.user import user_service
from api.v1.models import *

terms_and_conditions = APIRouter(
    prefix="/terms-and-conditions", tags=["Terms and Conditions"]
)

@terms_and_conditions.get("/{id}", response_model=success_response, status_code=200)
async def get_terms_and_conditions(
    id: str,
    db: Session = Depends(get_db)
):
    """Endpoint to get term and condition based on id"""
    tc = terms_and_conditions_service.fetch(db, id)
    if not tc:
        return success_response(
            message="Term and condition not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(
        data=tc.to_dict(),
        message="success",
        status_code=status.HTTP_200_OK
    )

@terms_and_conditions.patch("/{id}", response_model=success_response, status_code=200)
async def update_terms_and_conditions(
    id: str,
    schema: UpdateTermsAndConditions,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to update terms and conditions. Only accessible to superadmins"""

    tc = terms_and_conditions_service.update(db, id=id, data=schema)
    if not tc:
        return success_response(
            message="Terms and conditions not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(
        data=tc.to_dict(),
        message="Successfully updated terms and conditions",
        status_code=status.HTTP_200_OK,
    )
