from sqlalchemy.orm import Session
from api.v1.models.payment import Payment
from api.utils.db_validators import check_model_existence

class PaymentService:
    def get_payment_by_id(self, db: Session, payment_id: str):
        payment = check_model_existence(db, Payment, payment_id)
        return payment
