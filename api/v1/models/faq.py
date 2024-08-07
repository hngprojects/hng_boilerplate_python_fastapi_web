from sqlalchemy import Column, String, Text
from api.v1.models.base_model import BaseTableModel


class FAQ(BaseTableModel):
    __tablename__ = "faqs"

    question = Column(String, nullable=True)
    answer = Column(Text, nullable=True)
