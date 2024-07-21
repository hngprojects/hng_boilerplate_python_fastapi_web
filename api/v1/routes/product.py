from api.v1.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.product import Product
from api.utils.dependencies import get_current_user

product = APIRouter(prefix="/api/v1/products", tags=["product"])

@product.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Fetch the product to delete
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this product")

    db.delete(product)
    db.commit()

    return {"detail": "Product deleted successfully"}
