from api.v1.models.product import Product
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(
    prefix='/v1/products',
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

class Products(BaseModel):
    name: str
    price: float
    description: str | None=None

@router.post("/api/products")
async def add_product(products: Products):
    try:
        product = Product
        product.name = products.name
        product.description = products.description
        product.price = products.price
        product.user_id = 1
        return JSONResponse(content={"id": product.id, "product_name": product.name, "price": product.price, "description": product.description, "created_at": product.created_at, "updated_at":product.updated_at}, media_type="application/json", status_code=201)
    except:
        return JSONResponse({"statusCode:": 400,
        "message": ["name must be a string", "price must be a positive number"],
        "error": "Bad Request"
        })