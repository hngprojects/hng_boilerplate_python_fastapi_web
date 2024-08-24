from decimal import Decimal
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat, ConfigDict, StringConstraints

from typing import List, Optional
from datetime import datetime

class APIStatusPost(BaseModel):
    """
    Pydantic model for creating a new API status.

    This model is used for validating and serializing data when creating
    a new API status in the system. It ensures that the `status` field is a required
    string, the `description` is an optional string, and the `created_at` field
    is a datetime object that indicates when the API status was created.

    Attributes:
        status (str): The status of the API.
        description (Optional[str]): An optional description of the API status.
        created_at (datetime): The date and time when the API status was created.
    """

    api_group: str
    status: str
    response_time: Optional[Decimal] = None
    details: str

    class Config:
        from_attributes = True
        populate_by_name = True


class APIStatusUpdate(BaseModel):
    """
    Pydantic model for updating an existing API status.

    This model is used for validating and serializing data when updating
    an existing API status in the system. It ensures that the `status` field is a required
    string, the `description` is an optional string, and the `created_at` field
    is a datetime object that indicates when the API status was created.

    Attributes:
        status (str): The status of the API.
        description (Optional[str]): An optional description of the API status.
        created_at (datetime): The date and time when the API status was created.
    """

    api_group: str = Field(..., alias="apiGroup")
    status: str
    last_checked: Optional[datetime] = None
    response_time: Optional[Decimal] = None
    details: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True