# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from app.db.database import SessionLocal, engine
import app.models as models
import app.schemas as schemas
import app.auth as auth
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/v1/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "status": "success",
        "message": "Product details retrieved successfully",
        "status_code": 200,
        "data": product
    }
