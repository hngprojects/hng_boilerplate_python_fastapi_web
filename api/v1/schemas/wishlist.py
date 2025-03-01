from pydantic import BaseModel
from datetime import datetime


class WishlistCreate(BaseModel):
	product_id: str


class WishlistResponse(BaseModel):
	id: str
	user_id: str
	product_id: str
	created_at: datetime

	class Config:
		from_attributes = True