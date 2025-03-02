from sqlalchemy import Column, String, ForeignKey, DateTime,func
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel
from api.v1.models import User, Product


class Wishlist(BaseTableModel):
	__tablename__ = 'wishlists'

	user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
	created_at = Column(DateTime, server_default=func.now())

	user = relationship("User", back_populates="wishlist")
	product = relationship("Product")

	def __str__(self):
		return f"Wishlist(User: {self.user_id}, Product: {self.product_id})"
	
