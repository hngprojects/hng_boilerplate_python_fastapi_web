from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.v1.models import User
from api.v1.models.payment import Payment
from api.utils.db_validators import check_model_existence


class PaymentService:
    """Payment service functionality"""

    def create(self, db: Session, schema):
        """Create a new payment"""

        new_payment = Payment(**schema)
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        return new_payment

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all payments with option to search using query parameters"""

        query = db.query(Payment)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Payment, column) and value:
                    query = query.filter(getattr(Payment, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, payment_id: str):
        """Fetches a payment by id"""

        payment = check_model_existence(db, Payment, payment_id)
        return payment

    def get_payment_by_id(self, db: Session, payment_id: str):
        payment = check_model_existence(db, Payment, payment_id)
        return payment

    def get_payment_by_transaction_id(self, db: Session, transaction_id: str):
        try:
            payment = db.query(Payment).filter(Payment.transaction_id==transaction_id).first()
            return payment
        except Exception:
            raise HTTPException(status_code=404, detail='Payment record not found in the database')

    def fetch_by_user(self, db: Session, user_id, limit, page):
        """Fetches all payments of a user"""

        # check if user exists
        _ = check_model_existence(db, User, user_id)

        # calculating offset value
        # from page and limit given
        offset_value = (page - 1) * limit

        # Filter to return only payments of the user_id
        payments = (
            db.query(Payment)
            .filter(Payment.user_id == user_id)
            .offset(offset_value)
            .limit(limit)
            .all()
        )

        return payments

    def update(self, db: Session, payment_id: str, schema):
        """Updates a payment"""

        payment = self.fetch(db=db, payment_id=payment_id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)

        db.commit()
        db.refresh(payment)
        return payment

    def delete(self, db: Session, payment_id: str):
        """Deletes a payment"""

        payment = self.fetch(db=db, payment_id=payment_id)
        db.delete(payment)
        db.commit()
