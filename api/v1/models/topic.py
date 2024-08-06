from sqlalchemy import Column, String, ForeignKey, Text, Float, ARRAY
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Topic(BaseTableModel):
    __tablename__ = 'topics'

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
