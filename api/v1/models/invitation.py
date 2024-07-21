from sqlalchemy import (
    Column,
    ForeignKey,
    Boolean,
    DateTime,
)
from api.db.database import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID


# Invitation model
class Invitation(BaseModel, Base):
    __tablename__ = "invitations"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_valid = Column(Boolean, default=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
