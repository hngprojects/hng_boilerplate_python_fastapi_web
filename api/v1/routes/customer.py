from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from api.db.database import get_db
from ..schemas.customer import CustomerResponse
from api.v1.models.customer import Customer
from api.v1.models.user import User
from api.utils.dependencies import get_current_admin

customer_router = APIRouter(prefix='/api/v1', tags=['customers'])

class CustomerNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this action")

class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

@customer_router.delete('/customers/{customer_id}', response_model=CustomerResponse)
async def delete_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: Optional[User] = Depends(get_current_admin)
):
    try:
        if not current_admin:
            raise UnauthorizedException()
        
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not db_customer:
            raise CustomerNotFoundException()
        
        if db_customer.is_deleted:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already deleted")

        db_customer.is_deleted = True
        db.commit()
        db.refresh(db_customer)

        return db_customer

    except CustomerNotFoundException as e:
        raise e
    except UnauthorizedException as e:
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise DatabaseException(detail=str(e))
