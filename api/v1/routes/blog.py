from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.blog import (BlogCreate, BlogPostResponse, BlogRequest,
                                BlogUpdateResponseModel)
from api.v1.services.blog import BlogService
from api.v1.services.user import user_service

blog = APIRouter(prefix="/blogs", tags=["Blog"])

@blog.post("/", response_model=success_response)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_super_admin)):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not Authorized")
    blog_service = BlogService(db)
    new_blogpost = blog_service.create(db=db, schema=blog, author_id=current_user.id)

    return success_response(
        message = "Blog created successfully!",
        status_code = 200,
        data = jsonable_encoder(new_blogpost)
    )

@blog.get("/", response_model=success_response)
def get_all_blogs(db: Session = Depends(get_db)):

    blog_service = BlogService(db)
    blogs = blog_service.fetch_all()

    return success_response(
        message = "Blogs fetched successfully!",
        status_code = 200,
        data = [blog.to_dict() for blog in blogs]
    )


@blog.get("/{id}", response_model=BlogPostResponse)
def get_blog_by_id(id: str, db: Session = Depends(get_db)):
    """
    Retrieve a blog post by its Id.

    Args:
        id (str): The ID of the blog post.
        db (Session): The database session.

    Returns:
        BlogPostResponse: The blog post data.

    Raises:
        HTTPException: If the blog post is not found.
    """
    blog_service = BlogService(db)

    blog_post = blog_service.fetch(id)

    return success_response(
        message = "Blog post retrieved successfully!",
        status_code = 200,
        data = jsonable_encoder(blog_post)
    )


@blog.put("/{id}", response_model=BlogUpdateResponseModel)
async def update_blog(id: str, blogPost: BlogRequest, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_super_admin)):
    '''Endpoint to update a blog post'''

    blog_service = BlogService(db)
    updated_blog_post = blog_service.update(
        blog_id=id,
        title=blogPost.title,
        content=blogPost.content,
        current_user=current_user
    )
    
    return success_response(
        message = "Blog post updated successfully",
        status_code = 200,
        data = jsonable_encoder(updated_blog_post)
    )
    
    
@blog.delete("/{id}", status_code=204)
async def delete_blog_post(id: str, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_super_admin)):
    '''Endpoint to delete a blog post'''

    blog_service = BlogService(db=db)
    blog_service.delete(blog_id=id)
