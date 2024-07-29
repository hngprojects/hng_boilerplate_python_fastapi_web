from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.blog import (BlogCreate, BlogPostResponse, BlogRequest,
                                BlogUpdateResponseModel)
from api.v1.services.blog import BlogService
from api.v1.services.user import user_service
from api.v1.schemas.comment import CommentCreate, CommentSuccessResponse
from api.v1.services.comment import comment_service 

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

# Post a comment to a blog
@blog.post("/{blog_id}/comments", response_model=CommentSuccessResponse)
async def add_comment_to_blog(
    blog_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    comment: CommentCreate, 
    db: Annotated[Session, Depends(get_db)]
    ) -> Response:
    """Post endpoint for authenticated users to add comments to a blog. 

    Args:
        blog_id (str): the id of the blog to be commented on
        current_user: the current authenticated user 
        comment (CommentCreate): the body of the request
        db: the database session object

    Returns:
        Response: a response object containing the comment details if successful or appropriate errors if not
    """

    user_id = current_user.id
    new_comment = comment_service.create(db=db, schema=comment, user_id=user_id, blog_id=blog_id)

    return success_response(
        message = "Comment added successfully!",
        status_code = 201,
        data = jsonable_encoder(new_comment)
    )