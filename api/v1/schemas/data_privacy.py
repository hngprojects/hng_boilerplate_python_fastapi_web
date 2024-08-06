from pydantic import BaseModel
from typing import Optional

# profile_visibility = Column(Boolean, server_default='true')
#     share_data_with_partners = Column(Boolean, server_default='false')
#     receice_email_updates = Column(Boolean, server_default='true')
#     enable_two_factor_authentication = Column(Boolean, server_default='false')
#     use_data_encryption = Column(Boolean, server_default='true')
#     allow_analytics = Column(Boolean, server_default='true')
#     personalized_ads = Column(Boolean, server_default='false')
#

class DataPrivacySettingUpdate(BaseModel):
    profile_visibility: bool
    share_data_with_partners: bool
    receice_email_updates: bool
    enable_two_factor_authentication: bool
    use_data_encryption: bool
    allow_analytics: bool
    personalized_ads: bool

    class Config:
        from_attributes = True
        populate_by_name = True
