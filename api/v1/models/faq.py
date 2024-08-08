from sqlalchemy import Column, String, Text
from api.v1.models.base_model import BaseTableModel


class FAQ(BaseTableModel):
    __tablename__ = "faqs"

    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, nullable=True)
