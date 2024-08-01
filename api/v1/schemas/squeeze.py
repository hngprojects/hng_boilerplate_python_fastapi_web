from pydantic import BaseModel, EmailStr
from enum import Enum

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


class FilterSqueeze(BaseModel):
    status: SqueezeStatusEnum = None
