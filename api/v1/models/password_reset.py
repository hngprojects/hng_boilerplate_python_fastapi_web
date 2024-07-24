from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from api.v1.models.base import user_password_reset_otp_association
from api.v1.models.base_model import BaseTableModel
from datetime import datetime, timedelta


class OTP(BaseTableModel):
    __tablename__ = "otps"

    email = Column(String, index=True, nullable=False)
    otp_code = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))

    user = relationship("User", secondary=user_password_reset_otp_association, back_populates="users")

    def __init__(self, email: str, otp_code: int):
        self.email = email
        self.otp_code = otp_code
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(minutes=10)
