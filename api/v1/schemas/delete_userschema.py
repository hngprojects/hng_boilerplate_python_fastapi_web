from pydantic import BaseModel
from uuid import UUID



class UserDelete(BaseModel):
    user_id: UUID
    organization_id:UUID


class ResponseModel(BaseModel):
    message: str
    status_code: int