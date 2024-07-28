from sqlalchemy.orm import Session
from api.v1.models.payment import Payment

class PaymentService:
    def get_payment_by_id(self, db: Session, payment_id: str):
        return db.query(Payment).filter(Payment.id == payment_id).first()
