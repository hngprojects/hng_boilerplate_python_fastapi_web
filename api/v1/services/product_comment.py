

from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from api.core.base.services import Service
from api.v1.models import ProductComment, User
from api.db.database import get_db
from api.v1.schemas.product import ProductDeletionResponse

class ProductCommentService(Service):
    """
    Product comment service class
    """
    def delete(self, comment_id: str, product_id: str, user: User,
               db: Annotated[Session, Depends(get_db)]):
        """
        Deletes a comment linked to a product.
        Args:
            comment_id: the comment to delete
            product_id: the product the comment is linked to
            user: the current user
            db: the database Session object
        Returns:
            ProductDeletionResponse: response
        """
        comment_to_delete = db.query(ProductComment).filter_by(id=comment_id,
                                                               product_id=product_id,
                                                               user_id=user.id).first()
        if not comment_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='comment not found')
        
        db.delete(comment_to_delete)
        db.commit()
        return ProductDeletionResponse(status_code=status.HTTP_200_OK,
                                       status='success',
                                       message='comment successfully deleted')
    
    def create(self):
        pass
    
    def update(self):
        pass
    
    def fetch(self):
        pass
    
    def fetch_all(self):
        pass

product_comment_service = ProductCommentService()
