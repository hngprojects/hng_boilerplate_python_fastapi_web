from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Region(BaseTableModel):
    __tablename__ = "regions"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    region = Column(String, nullable=False)
    language = Column(String, nullable=True)
    timezone = Column(String, nullable=True)

    user = relationship("User", back_populates="region")