from pydantic import BaseModel
from datetime import datetime



class ReportCreateSchema(BaseModel):
    reported_user: str
    reason: str


class ReportResponseSchema(BaseModel):
    reported_by: str
    reported_user: str
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime
