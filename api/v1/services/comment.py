#api/v1/services/comment.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.v1.models.comment import Comment
from api.v1.schemas.comment import UpdateCommentRequest, UpdateCommentResponse
from typing import Any, Optional

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models import Comment, Blog, User

class CommentService(Service):
    '''Comment service functionality'''
    
    @staticmethod
    def update_comment(db: Session, comment_id: str, data: UpdateCommentRequest, user_id: str):
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found.")
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to update this comment.")
        comment.content = data.content
        db.commit()
        db.refresh(comment)
        return UpdateCommentResponse(
            status="success",
            message="Comment updated successfully.",
            status_code=200,
            data={"comment_id": comment.id, "content": comment.content, "updated_at": comment.updated_at}
        )

    def create(self, db: Session, schema, user_id, blog_id):
        '''Create a new comment to a blog'''
        # check if blog exists
        blog = check_model_existence(db, Blog, blog_id)

        # create and add the new comment to the database
        new_comment = Comment(**schema.model_dump(), user_id=user_id, blog_id=blog_id)
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment
    
    
    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all comments with option to search using query parameters'''
        '''Fetch all comments with option to search using query parameters'''
        query = db.query(Comment)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Comment, column) and value:
                    query = query.filter(getattr(Comment, column).ilike(f'%{value}%'))

        return query.all()
    
    def fetch(self, db: Session, id: str):
        '''Fetches a comment by id'''
        comment = check_model_existence(db, Comment, id)
        return comment

    def update(self, db: Session, id: str, schema):
        '''Updates a comment'''
        comment = self.fetch(db=db, id=id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(comment, key, value)
        
        db.commit()
        db.refresh(comment)
        return comment
    
    
    def delete(self, db: Session, id: str):
        '''Deletes a comment'''
        comment = self.fetch(id=id)
        db.delete(comment)
        db.commit()


comment_service = CommentService()
