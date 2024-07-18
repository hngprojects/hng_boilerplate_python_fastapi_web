import uuid
import datetime

from sqlalchemy import Column, String, DateTime
from api.db.database import Base


class Article(Base):
    __tablename__ = "articles_table"
    article_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, unique=True, nullable=False)
    content = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
