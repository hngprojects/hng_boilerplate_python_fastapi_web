from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FeatureRequestBase(BaseModel):
    title: str = Field(..., description="Title of the feature request")
    description: str = Field(..., description="Detailed description of the requested feature")
    priority: str = Field(default="Low", description="Priority level (Low, Medium, High)")
    status: str = Field(default="Pending", description="Status (Pending, Approved, Rejected)")


class FeatureRequestCreate(FeatureRequestBase):
    pass


class FeatureRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Title of the feature request")
    description: Optional[str] = Field(None, description="Detailed description of the requested feature")
    priority: Optional[str] = Field(None, description="Priority level (Low, Medium, High)")
    status: Optional[str] = Field(None, description="Status (Pending, Approved, Rejected)")


class FeatureRequestInDB(FeatureRequestBase):
    id: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    is_deleted: bool = False

    class Config:
        orm_mode = True


class FeatureRequestResponse(FeatureRequestInDB):
    pass