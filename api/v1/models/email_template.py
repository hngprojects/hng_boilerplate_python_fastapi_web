from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class EmailTemplate(BaseTableModel):
    __tablename__ = "email_templates"

    name = Column(Text, nullable=False)
    html_content = Column(Text, nullable=False)