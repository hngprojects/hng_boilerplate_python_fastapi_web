

from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session
from typing import Annotated

from api.db.database import get_db
from api.v1.services.product_comment import product_comment_service
from api.v1.services.user import user_service, User

product_comment = APIRouter(prefix="/products/{product_id}/comments", tags=["Product Comments"])


@product_comment.delete('/{comment_id}', status_code=status.HTTP_200_OK)
async def delete_product_comment(product_id: str, comment_id: str,
                                 db: Annotated[Session, Depends(get_db)],
                                 user: Annotated[User, Depends(user_service.get_current_user)]):
    """
    Deletes a comment attached to a product.
    Args:
        product_id: the product the comment is attached to
        comment_id: the comment to delete
        db: the database Session object
        user: the current user making the request
    Returns:
        successful response
    """
    return product_comment_service.delete(comment_id, product_id, user, db)
