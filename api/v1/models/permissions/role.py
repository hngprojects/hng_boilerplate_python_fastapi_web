from sqlalchemy import Column, String, Boolean, Text
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7

class Role(BaseTableModel):
    __tablename__ = 'roles'

    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_builtin = Column(Boolean, default=False)  # True for built-in roles, False for custom roles
