from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Region(BaseTableModel):
    __tablename__ = "regions"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    user = relationship("User", back_populates="region")

class Language(BaseTableModel):
    __tablename__ = "languages"

    name = Column(String, nullable=False)

class Timezone(BaseTableModel):
    __tablename__ = "timezones"

    name = Column(String, nullable=False)
