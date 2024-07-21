from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.product import Product
from api.v1.models.user import User
from api.utils.dependencies import get_current_admin

product = APIRouter(prefix="/products", tags=["products"])

@product.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    current_admin: Annotated[User, Depends(get_current_admin)],
    product_id: str,
    db: Session = Depends(get_db),
):
    # Fetch the product to delete
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()

    return {
        "status": "success",
        "message": "Product deleted successfully"
    }