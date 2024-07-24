from fastapi import Depends, status, APIRouter, Response, Request
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
# from api.v1.models import User
# from typing import Annotated
# from datetime import timedelta
from api.v1.schemas.user import UserCreate
from api.db.database import get_db
from api.v1.schemas.products import ProductSchema

# from api.v1.services.user import user_service
from api.v1.services.product import ProductService
from api.v1.models.product import Product

product = APIRouter(prefix="/product/create", tags=["Product"])

@product.post("/", status_code=status.HTTP_200_OK)
async def create_product(request:Request, data: ProductSchema, db: Session = Depends(get_db)):
    '''Endpoint to log in a user'''

    # Authenticate the user
    # Product.created_at
    
    # product = ProductService()
    # product.create(db=db, schema=data)
    print(data)


    response = success_response(
        status_code=200,
        message='Product created successfully',
        data = {}
    )

    # Add refresh token to cookies

    return response



