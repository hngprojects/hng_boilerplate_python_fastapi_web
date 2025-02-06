from sqlalchemy import (Column, Integer, Float,
                        ForeignKey, Index, String)
from sqlalchemy.orm import relationship

from api.v1.models.base_model import BaseTableModel


class Sales(BaseTableModel):
    __tablename__ = 'sales'
    quantity = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    product_id = Column(String, ForeignKey('products.id', ondelete='CASCADE'),
                        nullable=False)
    organisation_id = Column(String, ForeignKey('organisations.id', ondelete='CASCADE'),
                             nullable=False)
    payment_id = Column(String, ForeignKey('payments.id', ondelete='CASCADE'),
                             nullable=True)




    product = relationship("Product", back_populates="sales")
    organisation = relationship("Organisation", back_populates="sales")
    payment = relationship("Payment", back_populates="sales")
   
    __table_args__ = (
        Index('idx_sales_created_at', 'created_at'),
    )
