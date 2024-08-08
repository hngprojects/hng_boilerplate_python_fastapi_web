from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.v1.models.product import ProductComment
from api.v1.schemas.product_comment import ProductCommentCreate, ProductCommentUpdate


class ProductCommentService:
    def create(self, db: Session, schema: ProductCommentCreate, user_id: str, product_id: str, org_id: str):
            product_comment = ProductComment(
                product_id=product_id,
                user_id=user_id,
                content=schema.content
            )
            db.add(product_comment)
            db.commit()
            db.refresh(product_comment)
            return product_comment

    def fetch_single(self, db: Session, comment_id: str):
        product_comment = db.query(ProductComment).filter(ProductComment.id == comment_id).first()
        if not product_comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        return product_comment

    def fetch_all(self, db: Session, product_id: str):
        return db.query(ProductComment).filter(ProductComment.product_id == product_id).all()

    def update(self, db: Session, comment_id: str, schema: ProductCommentUpdate):
        product_comment = self.fetch_single(db, comment_id)
        for key, value in schema.dict(exclude_unset=True).items():
            setattr(product_comment, key, value)
        db.commit()
        db.refresh(product_comment)
        return product_comment

    def delete(self, db: Session, comment_id: str):
        product_comment = self.fetch_single(db, comment_id)
        db.delete(product_comment)
        db.commit()


product_comment_service = ProductCommentService()
