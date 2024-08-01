from api.db.database import get_db
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
        pass


