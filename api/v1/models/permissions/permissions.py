from sqlalchemy import Column, String
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7

class Permission(BaseTableModel):
    __tablename__ = 'permissions'

    #id = Column(String, primary_key=True, index=True, default=lambda: str(uuid7()))
    title = Column(String, unique=True, nullable=False)
    
