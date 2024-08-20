from sqlalchemy import Boolean, Column, Text, String, Enum
from api.v1.models.base_model import BaseTableModel


class EmailTemplate(BaseTableModel):
    __tablename__ = "email_templates"

    title = Column(Text, nullable=False)
    template = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    template_status = Column(Enum('online', 'offline', name='template_status'), server_default='online')
