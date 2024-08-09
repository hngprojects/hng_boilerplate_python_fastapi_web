from fastapi import Depends, APIRouter, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Annotated
from typing import List

from api.utils.pagination import paginated_response
from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.models.product import Product, ProductFilterStatusEnum, ProductStatusEnum
from api.v1.services.product import product_service, ProductCategoryService

from api.utils.dependencies import get_current_user
from api.v1.schemas.product import ProductCommentsSchema, ProductCommentCreate
from api.v1.schemas.product_comment import (
    ProductCommentResponse,
    ProductCommentUpdate,
)
from api.v1.services.product_comment import product_comment_service
from api.v1.services.user import user_service
from api.v1.models import User

product_comment = APIRouter(
    prefix="/products/{product_id}/comments", tags=["Product Comments"]
)


@product_comment.get(
    "/{comment_id}",
    response_model=ProductCommentResponse,
    status_code=status.HTTP_200_OK,
)
def get_product_comment(
    product_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """An endpoint that fetches a single product comment"""
    comment = product_comment_service.fetch(db=db, id=comment_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Comment fetched successfully",
        data=jsonable_encoder(comment),
    )


@product_comment.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductCommentsSchema,
)
def create_product_comment(
    product_id: str,
    comment: ProductCommentCreate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    product_comment = product_comment_service.create(
        db, comment, current_user.id, product_id
    )
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Product Comment successfully created",
        data=jsonable_encoder(product_comment),
    )


@product_comment.patch(
    "/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductCommentsSchema,
)
def update_product_comment(
    product_id: str,
    comment_id: str,
    comment: ProductCommentCreate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    product_comment = product_comment_service.update(db, comment_id, comment)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Product Comment successfully updated!",
        data=jsonable_encoder(product_comment),
    )


@product_comment.get(
    "",
    response_model=List[ProductCommentResponse],
    status_code=status.HTTP_200_OK,
)
@product_comment.get(
    "", response_model=List[ProductCommentResponse], status_code=status.HTTP_200_OK
)
def get_all_product_comments(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """An endpoint that fetches all product comment"""
    comments = product_comment_service.fetch_all(db=db, product_id=product_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Comments fetched successfully",
        data=jsonable_encoder(comments),
    )


@product_comment.delete("")
def delete_all_product_comments(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not Authorized")
    deleted_comment = product_comment_service.delete_product_comments(
        db=db, product_id=product_id
    )
    return success_response(
        message=deleted_comment["message"],
        status_code=200,
    )
