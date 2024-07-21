from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Boolean,
    Table,
)
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from api.v1.models.permission import Permission

user_role_association = Table(
    "user_role",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

role_permission_association = Table(
    "role_permission",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(BaseModel, Base):
    __tablename__ = "roles"

    role_name = Column(String, index=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id',  ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)

    permissions = relationship(
        "Permission", secondary=role_permission_association, backref="roles"
    )
    organization = relationship("Organization", back_populates="roles")
    users = relationship("User", secondary=user_role_association, backref="roles")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
