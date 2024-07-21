from sqlalchemy import Column, String, DateTime
from api.db.database import Base
from datetime import datetime

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime)
