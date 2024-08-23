""" The Profile model
"""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Profile(BaseTableModel):
    __tablename__ = "profiles"

    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    username = Column(String, nullable=True)
    pronouns = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    department = Column(String, nullable=True)
    social = Column(Text, nullable=True)  # Assuming JSON or similar data type
    bio = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    recovery_email = Column(String, nullable=True)
    facebook_link = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)
    twitter_link = Column(String, nullable=True)
    linkedin_link = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "id": self.id,
            "pronouns": self.pronouns,
            "job_title": self.job_title,
            "department": self.department,
            "social": self.social,
            "bio": self.bio,
            "phone_number": self.phone_number,
            "avatar_url": self.avatar_url,
            "recovery_email": self.recovery_email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
