from api.core.base.services import Service
from sqlalchemy.orm import Session
from api.v1.schemas.reply import ReplyCreate
from api.v1.models.reply import Reply


class ReplyService(Service):
    """
    CRUD class for the reply service
    """ 
    
    def create(self, db: Session, schema: ReplyCreate, comment_id: str, user_id: str):
        """
        creates new reply
        """
        reply = Reply(**schema.model_dump(), user_id=user_id, comment_id=comment_id)
        db.add(reply)
        db.commit()
        db.refresh(reply)
        
        return reply
    
    def fetch(self, db: Session):
        super().fetch()

    def fetch_all(self):
        super().fetch_all()

    def update(self):
        super().update()

    def delete(self):
        return super().delete()
    
    
reply_service = ReplyService()