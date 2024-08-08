from sqlalchemy import Column, String, Text
from api.v1.models.base_model import BaseTableModel


class TermsAndConditions(BaseTableModel):
    __tablename__ = "terms_and_conditions"

    title = Column(String)
    content = Column(Text)