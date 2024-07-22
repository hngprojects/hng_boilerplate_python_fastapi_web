from typing import Optional
from pydantic import BaseModel


class DeactivateUserSchema(BaseModel):
    '''Schema for deactivating a user'''

    reason: Optional[str] = None
    confirmation: bool
    