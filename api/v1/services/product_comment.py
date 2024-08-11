
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.core.base.services import Service
from typing import Any, Optional, Union, Annotated
from sqlalchemy import desc
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.utils.db_validators import check_model_existence
from api.v1.models.product import Product, ProductComment
from api.v1.schemas.comment import CommentsSchema, CommentsResponse


class ProductCommentService(Service):
    """Product ProductComment service functionality"""

    def create(self, db: Session, schema, user_id, product_id):
        """Create a new product comment to a product"""
        # check if product exists
        product = check_model_existence(db, Product, product_id)

        # create and add the new comment to the database
        new_comment = ProductComment(**schema.model_dump(), user_id=user_id, product_id=product_id)
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all product comments with option to search using query parameters"""

        query = db.query(ProductComment)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(ProductComment, column) and value:
                    query = query.filter(getattr(ProductComment, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a product comment by id"""

        comment = check_model_existence(db, ProductComment, id)
        return comment

    def update(self, db: Session, id: str, schema):
        """Updates a comment"""

        comment = self.fetch(db=db, id=id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(comment, key, value)

        db.commit()
        db.refresh(comment)
        return comment

    def delete(self, db: Session, id: str):
        """Deletes a comment"""

        comment = self.fetch(db=db, id=id)
        db.delete(comment)
        db.commit()

    def validate_params(
        self, product_id: str, page: int, per_page: int, db: Annotated[Session, get_db]
    ):
        """
        Validate parameters and fetch comments.

        Args:
            product_id: product associated with comments
            page: the number of the current page
            per_page: the page size for a current page
            db: Database Session object
        Returns:
            Response: An exception if error occurs
            object: Response object containing the comments
        """
        try:
            product_exists: Union[object, None] = (
                db.query(Product).filter_by(id=product_id).one_or_none()
            )
            if not product_exists:
                return "Product not found"
            per_page = per_page if per_page <= 20 else 20

            comments: Union[list, None] = (
                db.query(ProductComment)
                .filter_by(product_id=product_id)
                .order_by(desc(ProductComment.created_at))
                .limit(per_page)
                .offset((page - 1) * per_page)
                .all()
            )
            if not comments:
                return CommentsResponse()
            total_comments = db.query(ProductComment).filter_by(product_id=product_id).count()

            comment_schema: list = [
                CommentsSchema.model_validate(comment) for comment in comments
            ]
            return CommentsResponse(
                page=page, per_page=per_page, total=total_comments, data=comment_schema
            )
        except Exception:
            return False
        
    def delete_product_comments(self, db: Session, product_id: str):
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            deleted_count = db.query(ProductComment).filter(ProductComment.product_id == product_id).delete(synchronize_session=False)
            db.commit()

            return {"message": f"Deleted {deleted_count} comments for product with ID {product_id}"}
        
        except Exception as e:
            db.rollback()  
            raise HTTPException(status_code=500, detail=str(e))


product_comment_service = ProductCommentService()
