from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.organization import Organization
from api.v1.models.product import Product
from api.v1.schemas.product import ProductRequest, ProductResponse
from api.db.database import get_db
from api.utils.dependencies import get_current_user


# db = next(get_db())


product = APIRouter(tags=["products"])


@product.post("/api/v1/products", response_model=ProductResponse)
def get_product(request: ProductRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org_id = request.org_id
    product_id = request.pro_id

    # Check if the organization exists
    organization = db.query(Organization).filter(
        Organization.id == org_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if the product exists within the organization
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "status_code": 200,
        "message": f"Product {product.name} retrieved successfully",
        "data": product
    }
