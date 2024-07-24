""" The Profile model
"""
from sqlalchemy import (
        Column,
        String,
        Text,
        ForeignKey,
        )
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseTableModel



class Profile(BaseTableModel):
    __tablename__ = 'profiles'

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), unique=True, nullable=False)
    pronouns = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    department = Column(String, nullable=True)
    social = Column(Text, nullable=True)  # Assuming JSON or similar data type
    bio = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    recovery_email = Column(String, nullable=True)


    user = relationship("User", back_populates="profile")
