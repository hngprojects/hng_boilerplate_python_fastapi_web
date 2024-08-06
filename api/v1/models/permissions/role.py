from sqlalchemy import Column, String
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7

class Role(BaseTableModel):
    __tablename__ = 'roles'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid7()))
    name = Column(String, unique=True, nullable=False)
