from sqlalchemy import (
    Column,
    String,
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from api.v1.models.base_model import BaseModel

class Region(BaseModel, Base):
    __tablename__ = "regions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    region_code = Column(String(10), unique=True, nullable=False)
    region_name = Column(String(100), nullable=False)
    status = Column(String(10), nullable=False, default="active")
    created_on = Column(DateTime(timezone=True), server_default=func.now())
    modified_on = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    modified_by = Column(String(50), ForeignKey("users.username"), nullable=True)  
    created_by = Column(String(50), ForeignKey("users.username"), nullable=False) 
    creator = relationship(
        "User", back_populates="created_regions", foreign_keys=[created_by]
    )
    modifier = relationship("User", foreign_keys=[modified_by])
