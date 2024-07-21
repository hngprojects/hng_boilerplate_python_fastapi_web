from sqlalchemy import Column, String
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class Permission(BaseModel, Base):
    __tablename__ = "permissions"

    name = Column(String, unique=True, index=True, nullable=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
