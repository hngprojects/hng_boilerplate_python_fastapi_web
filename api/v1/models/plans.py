from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        ARRAY,
        JSON
        )
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from api.utils.settings import settings

class SubscriptionPlan(BaseModel, Base):
    __tablename__ = "plans"
    prod_env = settings.dev in ["prod", "dev"]
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    if prod_env:
        duration = Column(ARRAY(String), nullable=False)
        features = Column(ARRAY(String), nullable=False)
    else:
        duration = Column(JSON, nullable=False)
        features = Column(JSON, nullable=False)
