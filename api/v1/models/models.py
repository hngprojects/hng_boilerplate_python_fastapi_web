from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    company = Column(String)
    location = Column(String)
    salary = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
