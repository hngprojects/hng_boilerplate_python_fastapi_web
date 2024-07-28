from api.core.base.services import Service
from sqlalchemy.orm import Session
from api.v1.models.payment import Payment
from api.db.database import get_db
from api.v1.schemas.payment import CreatePaymentSchema
from api.utils.db_validators import check_model_existence
from secrets import token_hex
from typing import List, Optional, Any

class PaymentService(Service):
    '''Payment service functionality'''

    @staticmethod
    def create(db: Session,  schema: CreatePaymentSchema):
        '''Create a new payment'''

        new_payment = Payment(**schema.model_dump())
        new_payment.transaction_id = token_hex(16)
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        return new_payment

    @staticmethod    
    def fetch(db: Session, id: str) -> Payment:
        '''Fetches a payment record by id'''
        payment = check_model_existence(db, Payment, id)
        return payment

    @staticmethod
    def fetch_all(db: Session, **query_params: Optional[Any]) -> List[Payment]:
        '''Fetch all payments'''

        query = db.query(Payment)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Payment, column) and value:
                    query = query.filter(getattr(Payment, column).ilike(f'%{value}%'))

        return query.all()
    

