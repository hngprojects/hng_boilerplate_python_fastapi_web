from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class TokenLogin(BaseTableModel):
    __tablename__ = "token_logins"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), unique=True, nullable=False)
    token = Column(String, nullable=False)
    expiry_time = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="token_login")