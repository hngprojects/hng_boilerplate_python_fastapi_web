from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from api.v1.models.base_model import BaseTableModel
import api


class DataPrivacy(BaseTableModel):
    __tablename__ = "data_privacy"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped["api.v1.models.user.User"] = relationship(
        back_populates="data_privacy"
    )
    profile_visibility: Mapped[bool] = mapped_column(Boolean, default=True)
    share_data_with_partners: Mapped[bool] = mapped_column(Boolean, default=False)

    receive_email_updates: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_2fa: Mapped[bool] = mapped_column(Boolean, default=False)
    use_data_encryption: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_analytics: Mapped[bool] = mapped_column(Boolean, default=True)
    show_personalized_ads: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self) -> str:
        return self.user.username
