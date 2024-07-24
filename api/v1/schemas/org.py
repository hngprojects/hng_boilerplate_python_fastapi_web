# schema/organization_schema.py

from pydantic import BaseModel, Field
from typing import Optional

class OrganizationSchema(BaseModel):
    name: str = Field(..., description="The name of the organization")
    description: Optional[str] = Field(None, description="The description of the organization")

    class Config:
        orm_mode = True
