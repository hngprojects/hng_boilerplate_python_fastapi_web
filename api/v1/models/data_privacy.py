from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class DataPrivacySetting(BaseTableModel):
    __tablename__ = "data_privacy_settings"

    profile_visibility = Column(Boolean, server_default='true')
    share_data_with_partners = Column(Boolean, server_default='false')
    receice_email_updates = Column(Boolean, server_default='true')
    enable_two_factor_authentication = Column(Boolean, server_default='false')
    use_data_encryption = Column(Boolean, server_default='true')
    allow_analytics = Column(Boolean, server_default='true')
    personalized_ads = Column(Boolean, server_default='false')

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="data_privacy_setting")
