from sqlalchemy import Column, String, DateTime

from api.v1.models.base_model import BaseTableModel


class ContactMessage(BaseTableModel):
    __tablename__ = 'contact_messages'

    id = Column(String, primary_key=True, index=True)
    sender = Column(String, index=True)
    email = Column(String, index=True)
    message = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
