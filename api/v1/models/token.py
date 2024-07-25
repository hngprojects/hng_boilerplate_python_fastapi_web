from sqlalchemy import Column, String, Boolean, Float, DateTime
from api.db.database import Base

class Token(Base):
    __tablename__ = "tokens"

    token = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)
