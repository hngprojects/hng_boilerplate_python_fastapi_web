from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class SqueezeStatusEnum(str, Enum):
    online = "online"
    offline = "offline"


class CreateSqueeze(BaseModel):
    title: str
    email: EmailStr
    user_id: str
    url_slug: str = None
    headline: str = None
    sub_headline: str = None
    body: str = None
    type: str = "product"
    status: SqueezeStatusEnum = SqueezeStatusEnum.offline
    full_name: str = None



class UpdateSqueeze(BaseModel):
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    url_slug: Optional[str] = None
    headline: Optional[str] = None
    sub_headline: Optional[str] = None
    body: Optional[str] = None
    type: Optional[str] = None
    status: Optional[SqueezeStatusEnum] = None
    full_name: Optional[str] = None
