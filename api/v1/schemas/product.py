from pydantic import BaseModel
import datetime
import uuid


class ProductStock(BaseModel):
    productId: uuid.UUID
    currentStock: int
    lastUpdated: datetime.datetime
