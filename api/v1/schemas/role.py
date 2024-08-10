from pydantic import BaseModel
from typing import List


class RoleCreate(BaseModel):
    role_name: str
    organisation_id: str
    permission_ids: List[str]


class ResponseModel(BaseModel):
    message: str
    status_code: int
