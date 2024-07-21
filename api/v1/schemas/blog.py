from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from uuid import UUID


def validate_uuid7(uuid: UUID) -> UUID:
    if uuid.version != 7:
        raise ValueError("UUID version 7 expected")
    return uuid


class BlogResponseSchema(BaseModel):
    """Schema for the blog post response."""

    id: UUID
    title: str
    excerpt: Optional[str]
    content: str
    image_url: Optional[str]
    tags: Optional[List[str]]

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
        }

    @field_validator("id")
    def check_uuid7(cls, value):
        return validate_uuid7(value)


class BlogCreateSchema(BaseModel):
    """Schema for creating a new blog post."""

    title: str = Field(
        ...,
        max_length=100,
        description="Title of the blog post",
    )
    excerpt: Optional[str] = Field(
        None, max_length=500, description="Short excerpt of the blog post"
    )
    content: str = Field(..., description="Content of the blog post")
    image_url: Optional[str] = Field(
        None, max_length=100, description="URL of the blog post image"
    )
    tags: Optional[List[str]] = Field(
        None, description="Tags associated with the blog post"
    )


class BlogUpdateSchema(BaseModel):
    title: Optional[str]
    excerpt: Optional[str]
    content: Optional[str]
    image_url: Optional[str]
    tags: Optional[List[str]]

    class Config:
        from_attributes = True


class DeleteBlogResponseSchema(BaseModel):
    message: str
    status_code: int
