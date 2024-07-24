from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        ARRAY
        )
from api.v1.models.base_model import BaseTableModel


class SubscriptionPlan(BaseTableModel):
    __tablename__ = "plans"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    duration = Column(String(50), nullable=False)
    features = Column(ARRAY(String), nullable=False)