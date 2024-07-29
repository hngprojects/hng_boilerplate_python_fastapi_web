from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.comment import Comment, CommentLike
from typing import Any, Optional
from sqlalchemy.orm import Session
from api.utils.db_validators import check_model_existence
from api.v1.models.blog import Blog


class CommentService(Service):
	'''Comment service functionality'''

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
		'''Fetch all comments with option tto search using query parameters'''

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