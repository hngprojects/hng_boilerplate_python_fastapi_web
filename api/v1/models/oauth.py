from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class OAuth(BaseTableModel):
    __tablename__ = "oauth"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), unique=True, nullable=False)
    provider = Column(String, nullable=False)
    sub = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)

    user = relationship("User", back_populates="oauth")