from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models import Comment, CommentLike
from api.v1.models.comment import Comment


class CommentLikeService(Service):
    """Comment like service functionality"""

    def create(self, db: Session, user_id, comment_id, client_ip: Optional[str] = None):
        '''Function to like a comment'''
        
        like_data = db.query(CommentLike).filter_by(user_id=user_id, comment_id=comment_id).first()
        if like_data:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="You've already liked this comment",
            )
        check_model_existence(db, Comment, comment_id)
        new_like = CommentLike(
            comment_id=comment_id, user_id=user_id, ip_address=client_ip
        )
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        return new_like

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all comment_like with option tto search using query parameters"""

        query = db.query(CommentLike)

        if query_params:
            for column, value in query_params.items():
                if hasattr(CommentLike, column) and value:
                    query = query.filter(
                        getattr(CommentLike, column).ilike(f"%{value}%")
                    )

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a comment_like by id"""

        comment_like = check_model_existence(db, CommentLike, id)
        return comment_like

    def update(self, db: Session, id: str, schema):
        """Updates a comment_like"""

        comment_like = self.fetch(db=db, id=id)

        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(comment_like, key, value)

        db.commit()
        db.refresh(comment_like)
        return comment_like

    def delete(self, db: Session, id: str):
        """Deletes a comment like"""

        comment = self.fetch(id=id)
        db.delete(comment)
        db.commit()


comment_like_service = CommentLikeService()
