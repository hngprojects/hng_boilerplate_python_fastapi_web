from enum import Enum
<<<<<<< Updated upstream
from typing import Optional

from pydantic import BaseModel, EmailStr

=======
from typing import Optional, Any, Dict
>>>>>>> Stashed changes

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


<<<<<<< Updated upstream
class UpdateSqueeze(BaseModel):
    title: Optional[str] = None
    headline: Optional[str] = None
    sub_headline: Optional[str] = None
    body: Optional[str] = None
    type: Optional[str] = None
    status: Optional[SqueezeStatusEnum] = None
    full_name: Optional[str] = None
=======
class SuccessResponseSchema(BaseModel):
    status_code: int
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
>>>>>>> Stashed changes
