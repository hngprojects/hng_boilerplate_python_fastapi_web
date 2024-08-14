from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from api.v1.models.base_model import BaseTableModel


class ResetPasswordToken(BaseTableModel):
    """
    Represents password reset tokens
    """
    __tablename__ = "reset_password_tokens"
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True)
    jti: Mapped[str] = mapped_column(String)
   
    user = relationship("User", back_populates="reset_password_token")
