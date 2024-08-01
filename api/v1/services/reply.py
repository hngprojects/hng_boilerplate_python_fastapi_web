from api.core.base.services import Service
from sqlalchemy.orm import Session
from api.v1.schemas.reply import ReplyCreate
from api.v1.models.reply import Reply


class ReplyService(Service):
    """
    """ 
    
    def create(self, db: Session, schema: ReplyCreate):
        """
        """
        reply = Reply(**schema.model_dump())
        db.add(reply)
        db.commit()
        db.refresh(reply)
        
        return reply