from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy import (
        Column,
        String,
        text,
        Boolean
        )

class Customer(BaseModel, Base):
    __tablename__ = 'customers'
    username = Column(String, nullable=False)
    email= Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    address = Column(String)
    password = Column(String, nullable=False, )
    is_active = Column(Boolean, server_default=text('true'))
    is_deleted = Column(Boolean, server_default=text('false'))
