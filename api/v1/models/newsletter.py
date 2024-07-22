from sqlalchemy import Column, String, DateTime
from uuid import uuid4
from datetime import datetime
from api.db.database import Base
from api.v1.models.base_model import BaseTableModel


class NEWSLETTER(BaseTableModel):
    """
    Newsletter db model
    """
    __tablename__ = 'newsletters'
    email = Column(String(150), unique=True, nullable=False)
 