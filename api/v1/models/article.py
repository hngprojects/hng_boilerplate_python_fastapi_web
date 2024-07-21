from api.db.database import Base
from api.v1.models.base_model import BaseModel
from uuid_extensions import uuid7
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY


class Article(BaseModel, Base):
    __tablename__ = "articles"

    title = Column(String, unique=True, nullable=False)
    content = Column(String, nullable=False)
