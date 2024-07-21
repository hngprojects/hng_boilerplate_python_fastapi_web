from sqlalchemy import Column, String
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel

class SuperAdmin(BaseModel, Base):
    __tablename__ = 'super_admins'

    name = Column(String, index=True, nullable=False)