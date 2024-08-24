from fastapi import APIRouter, Depends, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional

from api.db.database import get_db
from api.utils.pagination import paginated_response
from api.utils.success_response import success_response
from api.v1.models.faq import FAQ
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.faq import faq_service
from api.v1.schemas.faq import CreateFAQ, UpdateFAQ

faq = APIRouter(prefix="/faqs", tags=["Frequently Asked Questions"])


@faq.get("", response_model=success_response, status_code=200)
async def get_all_faqs(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, min_length=1)
):
    """Endpoint to get all FAQs or search by keyword in both question and answer"""

    query_params = {}
    if keyword:
        query_params["question"] = keyword
        query_params["answer"] = keyword

    grouped_faqs = faq_service.fetch_all_grouped_by_category(
        db=db, **query_params)

    return success_response(
        status_code=200,
        message="FAQs retrieved successfully",
        data=jsonable_encoder(grouped_faqs),
    )


@faq.post("", response_model=success_response, status_code=201)
async def create_faq(
    schema: CreateFAQ,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to create a new FAQ. Only accessible to superadmins"""

    faq = faq_service.create(db, schema=schema)

    return success_response(
        data=jsonable_encoder(faq),
        message="Successfully created FAQ",
        status_code=status.HTTP_201_CREATED,
    )


@faq.get("/{id}", response_model=success_response, status_code=200)
async def get_single_faq(id: str, db: Session = Depends(get_db)):
    """Endpoint to get a single FAQ"""

    faq = faq_service.fetch(db, faq_id=id)
    return success_response(
        data=jsonable_encoder(faq),
        message="Successfully fetched FAQ",
        status_code=status.HTTP_200_OK,
    )


@faq.patch("/{id}", response_model=success_response, status_code=200)
async def update_faq(
    id: str,
    schema: UpdateFAQ,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to update an FAQ. Only accessible to superadmins"""

    faq = faq_service.update(db, faq_id=id, schema=schema)

    return success_response(
        data=jsonable_encoder(faq),
        message="FAQ created successfully",
        status_code=status.HTTP_200_OK,
    )


@faq.delete("/{id}", status_code=200)
async def delete_faq(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to delete an FAQ. Only accessible to superadmins"""

    faq_service.delete(db, faq_id=id)

    return success_response(
        message="FAQ successfully deleted",
        status_code=200,
    )
