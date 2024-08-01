"""Squeeze page model."""

from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.orm import relationship
from enum import Enum


class SqueezeStatusEnum(str, Enum):
    online = "online"
    offline = "offline"


class Squeeze(BaseTableModel):
    __tablename__ = "squeezes"

    title = Column(String, nullable=False)
    email = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url_slug = Column(String, nullable=True)
    headline = Column(String, nullable=True)
    sub_headline = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    type = Column(String, nullable=True, default="product")
    full_name = Column(String, nullable=True)

    status = Column(
        SQLAlchemyEnum(SqueezeStatusEnum), default=SqueezeStatusEnum.offline
    )
    user = relationship("User", back_populates="squeeze")

    def __str__(self):
        return self.title
