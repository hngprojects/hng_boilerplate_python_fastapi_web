from typing import Optional
from pydantic import BaseModel


class DataPrivacyUpdate(BaseModel):
    """
    Pydantic model for data privacy update request.
    """

    profile_visibility: Optional[bool] = None
    share_data_with_partners: Optional[bool] = None
    receice_email_updates: Optional[bool] = None
    enable_two_factor_authentication: Optional[bool] = None
    use_data_encryption: Optional[bool] = None
    allow_analytics: Optional[bool] = None
    personalized_ads: Optional[bool] = None

    class Config:
        from_attributes = True
