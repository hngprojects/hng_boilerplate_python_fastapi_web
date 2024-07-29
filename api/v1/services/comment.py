from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.comment import Comment, CommentLike
from api.utils.success_response import success_response

class CommentService(Service):
	def create(self):
		pass

	def delete(self):
		pass

	def fetch(self, db: Session, comment_id: str):
		"""
			Fetch a comment by its ID.
		"""
		comment =  db.query(Comment).filter_by(id=comment_id).first()
		if not comment:
			raise HTTPException(status_code=404, detail="Post not found")
		return comment

	def update(self):
		pass

	def fetch_all(self):
		pass
	
	def like(self, db: Session, comment_id: str, user_id: str, user_ip: str):
		"""
	 		Like a comment by its ID.
		"""
		self.fetch(db,comment_id)
		existing_like = db.query(CommentLike).filter_by(user_id=user_id, comment_id=comment_id).first()
		if existing_like:
			raise HTTPException(status_code=200, detail="You've already liked this comment")

		# Create a new like
		new_like = CommentLike(user_id=user_id, comment_id=comment_id, ip_address=user_ip)
		db.add(new_like)
		db.commit()
		return new_like

comment_service = CommentService()