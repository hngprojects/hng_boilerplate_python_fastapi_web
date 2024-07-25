from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.payment import Payment


class PaymentService:
    '''Payment service functionality'''

    def __init__(self, db: Session):
        self.db = db

    def create(self, db: Session,  schema):
        '''Create a new product'''

        new_payment = Payment(**schema.model_dump())
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        return new_payment
    

    def fetch_all(self):
        '''Fetch all payments.'''

        query = self.db.query(Payment).all()

        
        return query

    
    def fetch(self, db: Session, id: str):
        '''Fetches a payment by it id'''

        payment = check_model_existence(self.db, Payment, id)
        return payment
    
    