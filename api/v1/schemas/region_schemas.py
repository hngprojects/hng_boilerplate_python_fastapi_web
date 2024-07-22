from pydantic import BaseModel, Field


class RegionBase(BaseModel):
    region_code: str = Field(..., max_length=10)
    region_name: str = Field(..., max_length=100)
    status: str = Field("active", max_length=10)


class RegionCreate(RegionBase):
    created_by: str


class RegionResponse(RegionBase):
    id: int

    class Config:
        from_attributes = True
