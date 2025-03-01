from api.utils.success_response import success_response, fail_response
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.models.wishlist import Wishlist
from api.v1.models.product import Product
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.schemas.wishlist import WishlistCreate
from api.v1.services.wishlist import wishlist_service, ProductAlreadyInWishlistException,ProductNotFoundException

wishlist= APIRouter(prefix="/wishlist", tags=["Wishlist"])

@wishlist.post("/", response_model=success_response)
def add_to_wishlist(wishlist_data: WishlistCreate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
	if current_user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
	else:
		try:
			wishlist_service.create(db, current_user.id, wishlist_data)
			return success_response(status_code=201, message="Product added to wishlist successfully")
		except ProductAlreadyInWishlistException:
			raise HTTPException(status_code=400, detail="Product already in wishlist")
		except ProductNotFoundException:
			raise HTTPException(status_code=404, detail="Product not found")
