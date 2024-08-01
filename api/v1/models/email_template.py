from sqlalchemy import Boolean, Column, Text
from api.v1.models.base_model import BaseTableModel


class EmailTemplate(BaseTableModel):
    __tablename__ = "email_templates"

    title = Column(Text, nullable=False)
    template = Column(Text, nullable=False)
    status = Column(Boolean, server_default='true')
