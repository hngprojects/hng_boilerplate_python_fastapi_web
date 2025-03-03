from datetime import datetime
from pydantic import BaseModel, Field

class SessionCreate(BaseModel):
    ip_address: str
    location: str = None
    device: str = None
    is_revoked: bool = False
    refresh_token: str
    expires_at: datetime