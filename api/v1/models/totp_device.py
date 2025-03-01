from api.v1.models.base_model import BaseTableModel
from sqlalchemy import Column, String, ForeignKey, Boolean 
from sqlalchemy.orm import relationship


class TOTPDevice(BaseTableModel):
    """
    Database model representing a TOTP device for two-factor authentication.
    
    This model stores the secret key used for generating TOTP codes, along with the confirmation status and the relationship to the user who owns the device.
    """
    __tablename__ = "totp_devices"
    
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    secret = Column(String, nullable=False)
    confirmed = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="totp_device")
    
    def __str__(self):
        if self.user:
            return f"{self.user.email}'s TOTP device"
        return f"TOTP device for user_id: {self.user_id}"