from api.utils.success_response import success_response, fail_response
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.core.base.services import Service
from api.v1.models.product import Product
from api.v1.models.wishlist import Wishlist
from api.v1.schemas.wishlist import WishlistCreate

class ProductAlreadyInWishlistException(Exception):
	pass

class ProductNotFoundException(Exception):
	pass


class WishlistService(Service):
	def create(self, db: Session, user_id: str, schema: WishlistCreate):
		existing_entry = db.query(Wishlist).filter(Wishlist.user_id == user_id, Wishlist.product_id == schema.product_id).first()

		if existing_entry:
			raise ProductAlreadyInWishlistException("Product already in wishlist",)
	
		product = db.query(Product).filter(Product.id == schema.product_id).first()
		if not product:
			raise ProductNotFoundException("Product not found")
		
		wishlist_entry = Wishlist(user_id=user_id, **schema.model_dump())
		db.add(wishlist_entry)
		db.commit()
		db.refresh(wishlist_entry)

		return wishlist_entry
	
	def delete(self):
		return super().delete()

	def fetch(self):
		return super().fetch()
	
	def fetch_all(self):
		return super().fetch_all()
	
	def update(self):
		return super().update()
	

wishlist_service = WishlistService()